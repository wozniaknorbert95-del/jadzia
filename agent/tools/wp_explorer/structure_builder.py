"""
Builder struktury projektu.

Buduje kompletny ProjectStructure JSON z wyników analizy.

Author: Jadzia Architect Team
Version: 1.1
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Literal, Optional

from .config import ExplorerConfig, get_config
from .models import (
    Asset,
    Dependency,
    DependencyGraph,
    FileInfo,
    FunctionDef,
    Hook,
    HookRegistry,
    PathConfig,
    ProjectMeta,
    ProjectStructure,
    RiskLevel,
    TaskMapping,
)

logger = logging.getLogger(__name__)


class StructureBuilder:
    """
    Buduje strukturę projektu z wyników analizy.
    
    Odpowiada za:
    - Budowanie grafu zależności
    - Kategoryzację hooków
    - Tworzenie mapowań zadań
    - Generowanie i walidację JSON
    """
    
    def __init__(self, config: Optional[ExplorerConfig] = None):
        """
        Inicjalizuje builder.
        
        Args:
            config: Konfiguracja (opcjonalna)
        """
        self.config = config or get_config()
    
    def _build_dependency_graph(
        self,
        files: List[FileInfo],
        dependencies: List[Dependency]
    ) -> DependencyGraph:
        """
        Buduje graf zależności z topological sort.
        
        Args:
            files: Lista plików
            dependencies: Lista zależności
            
        Returns:
            DependencyGraph
        """
        nodes = [f.path for f in files]
        
        # Find entry points (files not required by others)
        required_files = {d.target_file for d in dependencies}
        entry_points = ['functions.php', 'style.css']  # Default WP entry points
        
        # Add any other files that are not required
        for node in nodes:
            if node.endswith('.php') and node not in required_files:
                if node not in entry_points:
                    # Could be a template file
                    if 'template' in node.lower() or node.startswith('woocommerce/'):
                        entry_points.append(node)
        
        # Simple topological sort for load order
        load_order = self._topological_sort(nodes, dependencies)
        
        return DependencyGraph(
            nodes=nodes,
            edges=dependencies,
            entry_points=entry_points,
            load_order=load_order
        )
    
    def _topological_sort(
        self,
        nodes: List[str],
        dependencies: List[Dependency]
    ) -> List[str]:
        """
        Wykonuje topological sort dla kolejności ładowania.
        
        Args:
            nodes: Lista plików
            dependencies: Lista zależności
            
        Returns:
            Lista plików w kolejności ładowania
        """
        # Build adjacency list
        graph: Dict[str, List[str]] = {node: [] for node in nodes}
        in_degree: Dict[str, int] = {node: 0 for node in nodes}
        
        for dep in dependencies:
            if dep.source_file in graph and dep.target_file in nodes:
                graph[dep.source_file].append(dep.target_file)
                in_degree[dep.target_file] = in_degree.get(dep.target_file, 0) + 1
        
        # Find nodes with no incoming edges
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # If not all nodes are in result, there's a cycle
        if len(result) != len(nodes):
            logger.warning("Dependency cycle detected, returning partial order")
            # Add remaining nodes
            for node in nodes:
                if node not in result:
                    result.append(node)
        
        return result
    
    def _categorize_hooks(self, hooks: List[Hook]) -> HookRegistry:
        """
        Kategoryzuje hooki do odpowiednich grup.
        
        Args:
            hooks: Lista wszystkich hooków
            
        Returns:
            HookRegistry z pogrupowanymi hookami
        """
        registry = HookRegistry()
        
        for hook in hooks:
            # Dynamic hooks
            if hook.is_dynamic:
                registry.dynamic_hooks.append(hook)
                continue
            
            # AJAX handlers
            if hook.hook_name.startswith(('wp_ajax_', 'wp_ajax_nopriv_')):
                registry.ajax_handlers.append(hook)
                continue
            
            # WooCommerce hooks
            if hook.hook_name.startswith('woocommerce_'):
                registry.woocommerce_hooks.append(hook)
                continue
            
            # Regular actions/filters
            if hook.type == 'action':
                registry.actions.append(hook)
            else:
                registry.filters.append(hook)
        
        return registry
    
    def _build_task_mappings(self) -> List[TaskMapping]:
        """
        Buduje mapowania zadań z konfiguracji.
        
        Returns:
            Lista TaskMapping
        """
        mappings = []
        
        for mapping_data in self.config.default_task_mappings:
            try:
                mappings.append(TaskMapping(
                    keywords=mapping_data['keywords'],
                    files=mapping_data['files'],
                    risk_level=RiskLevel(mapping_data['risk_level']),
                    description=mapping_data.get('description')
                ))
            except Exception as e:
                logger.warning(f"Invalid task mapping: {e}")
        
        return mappings
    
    def _get_critical_files(self, files: List[FileInfo]) -> List[str]:
        """
        Zwraca listę plików krytycznych.
        
        Args:
            files: Lista plików
            
        Returns:
            Lista ścieżek plików krytycznych
        """
        return [f.path for f in files if f.risk_level == RiskLevel.CRITICAL]
    
    def _get_backup_required_files(self, files: List[FileInfo]) -> List[str]:
        """
        Zwraca listę plików wymagających backup przed modyfikacją.
        
        Args:
            files: Lista plików
            
        Returns:
            Lista ścieżek
        """
        return [
            f.path for f in files 
            if f.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
        ]
    
    def build(
        self,
        files: List[FileInfo],
        dependencies: List[Dependency],
        hooks: List[Hook],
        assets: List[Asset],
        functions: List[FunctionDef],
        scan_duration: float,
        source: Literal["manual", "post_deploy", "scheduled", "startup"] = "manual",
        trigger_file: Optional[str] = None
    ) -> ProjectStructure:
        """
        Buduje kompletną strukturę projektu.
        
        Args:
            files: Lista plików
            dependencies: Lista zależności
            hooks: Lista hooków
            assets: Lista assetów
            functions: Lista funkcji
            scan_duration: Czas skanowania w sekundach
            source: Źródło skanu
            trigger_file: Plik który wywołał skan (dla post_deploy)
            
        Returns:
            ProjectStructure
        """
        # Build components
        dependency_graph = self._build_dependency_graph(files, dependencies)
        hook_registry = self._categorize_hooks(hooks)
        task_mappings = self._build_task_mappings()
        
        # Calculate totals
        total_size = sum(f.size_kb for f in files)
        
        # Build files dict
        files_dict = {f.path: f for f in files}
        
        structure = ProjectStructure(
            project=ProjectMeta(
                name="ZZPackage WooCommerce Store",
                type="wordpress_woocommerce",
                architecture="legacy_child_theme",
                parent_theme="hello-theme"
            ),
            last_scan=datetime.now(timezone.utc),
            scan_duration_seconds=round(scan_duration, 2),
            scan_source=source,
            trigger_file=trigger_file,
            paths=PathConfig(
                base=self.config.wordpress_base_path,
                theme=self.config.theme_relative_path,
                theme_absolute=self.config.theme_absolute_path,
                url=self.config.shop_url
            ),
            files=files_dict,
            file_count=len(files),
            total_size_kb=round(total_size, 2),
            dependencies=dependency_graph,
            hooks=hook_registry,
            assets=assets,
            functions=functions,
            task_mappings=task_mappings,
            critical_files=self._get_critical_files(files),
            backup_required_files=self._get_backup_required_files(files)
        )
        
        return structure
    
    def save_structure(
        self,
        structure: ProjectStructure,
        output_path: Optional[str] = None
    ) -> str:
        """
        Zapisuje strukturę do pliku JSON.
        
        Args:
            structure: Struktura do zapisania
            output_path: Ścieżka wyjściowa (opcjonalna)
            
        Returns:
            Ścieżka do zapisanego pliku
        """
        output = Path(output_path or self.config.output_path)
        backup = Path(self.config.backup_path)
        
        # Ensure directory exists
        output.parent.mkdir(parents=True, exist_ok=True)
        
        # Backup existing file
        if output.exists():
            shutil.copy2(output, backup)
            logger.info(f"Backed up previous structure to {backup}")
        
        # Save new structure
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(
                structure.model_dump(mode='json'),
                f,
                indent=2,
                ensure_ascii=False,
                default=str
            )
        
        logger.info(f"Saved structure to {output}")
        return str(output)
    
    def load_structure(
        self,
        input_path: Optional[str] = None
    ) -> Optional[ProjectStructure]:
        """
        Ładuje strukturę z pliku JSON.
        
        Args:
            input_path: Ścieżka wejściowa (opcjonalna)
            
        Returns:
            ProjectStructure lub None jeśli nie istnieje
        """
        input_file = Path(input_path or self.config.output_path)
        
        if not input_file.exists():
            return None
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return ProjectStructure(**data)
            
        except Exception as e:
            logger.error(f"Failed to load structure: {e}")
            return None