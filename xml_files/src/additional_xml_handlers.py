#!/usr/bin/env python3
"""
Additional XML Handlers for Common Document Types

This module extends the specialized handler system with more document types
commonly found in enterprise environments.
"""

from xml_specialized_handlers import XMLHandler, DocumentTypeInfo, SpecializedAnalysis
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any, Tuple
import re
from datetime import datetime

class MavenPOMHandler(XMLHandler):
    """Handler for Maven Project Object Model (POM) files"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # Check if root is 'project' and has Maven namespace
        if root.tag == 'project' or root.tag.endswith('}project'):
            if 'maven.apache.org' in str(namespaces.values()):
                return True, 1.0
            # Even without namespace, if it has Maven-like structure
            if root.find('.//groupId') is not None and root.find('.//artifactId') is not None:
                return True, 0.8
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        pom_version = root.find('.//modelVersion')
        version = pom_version.text if pom_version is not None else "4.0.0"
        
        return DocumentTypeInfo(
            type_name="Maven POM",
            confidence=1.0,
            version=version,
            schema_uri="http://maven.apache.org/POM/4.0.0",
            metadata={
                "build_tool": "Maven",
                "category": "build_configuration"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            'project_info': self._extract_project_info(root),
            'dependencies': self._analyze_dependencies(root),
            'plugins': self._analyze_plugins(root),
            'repositories': self._extract_repositories(root),
            'properties': self._extract_properties(root)
        }
        
        recommendations = [
            "Analyze dependency tree for security vulnerabilities",
            "Check for outdated dependencies",
            "Extract for software composition analysis",
            "Monitor for license compliance"
        ]
        
        ai_use_cases = [
            "Dependency vulnerability detection",
            "License compliance checking",
            "Technical debt analysis",
            "Build optimization recommendations",
            "Dependency update suggestions"
        ]
        
        data_inventory = {
            'dependencies': len(findings['dependencies']['all']),
            'plugins': len(findings['plugins']),
            'properties': len(findings['properties'])
        }
        
        return SpecializedAnalysis(
            document_type="Maven POM",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory=data_inventory,
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._calculate_pom_quality(findings)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'coordinates': {
                'groupId': getattr(root.find('.//groupId'), 'text', None),
                'artifactId': getattr(root.find('.//artifactId'), 'text', None),
                'version': getattr(root.find('.//version'), 'text', None),
                'packaging': getattr(root.find('.//packaging'), 'text', 'jar')
            },
            'dependencies': self._extract_dependency_list(root),
            'build_config': self._extract_build_config(root)
        }
    
    def _extract_project_info(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'name': getattr(root.find('.//name'), 'text', None),
            'description': getattr(root.find('.//description'), 'text', None),
            'url': getattr(root.find('.//url'), 'text', None),
            'parent': self._extract_parent_info(root)
        }
    
    def _analyze_dependencies(self, root: ET.Element) -> Dict[str, Any]:
        deps = root.findall('.//dependency')
        
        scopes = {}
        for dep in deps:
            scope = getattr(dep.find('.//scope'), 'text', 'compile')
            scopes[scope] = scopes.get(scope, 0) + 1
        
        return {
            'all': [self._extract_dependency(d) for d in deps],
            'count': len(deps),
            'by_scope': scopes,
            'management': len(root.findall('.//dependencyManagement//dependency'))
        }
    
    def _analyze_plugins(self, root: ET.Element) -> List[Dict[str, str]]:
        plugins = []
        for plugin in root.findall('.//plugin'):
            plugins.append({
                'groupId': getattr(plugin.find('.//groupId'), 'text', 'org.apache.maven.plugins'),
                'artifactId': getattr(plugin.find('.//artifactId'), 'text', None),
                'version': getattr(plugin.find('.//version'), 'text', None)
            })
        return plugins
    
    def _extract_repositories(self, root: ET.Element) -> List[Dict[str, str]]:
        repos = []
        for repo in root.findall('.//repository'):
            repos.append({
                'id': getattr(repo.find('.//id'), 'text', None),
                'url': getattr(repo.find('.//url'), 'text', None)
            })
        return repos
    
    def _extract_properties(self, root: ET.Element) -> Dict[str, str]:
        props = {}
        properties = root.find('.//properties')
        if properties is not None:
            for prop in properties:
                props[prop.tag] = prop.text
        return props
    
    def _extract_parent_info(self, root: ET.Element) -> Optional[Dict[str, str]]:
        parent = root.find('.//parent')
        if parent is None:
            return None
        return {
            'groupId': getattr(parent.find('.//groupId'), 'text', None),
            'artifactId': getattr(parent.find('.//artifactId'), 'text', None),
            'version': getattr(parent.find('.//version'), 'text', None)
        }
    
    def _extract_dependency(self, dep: ET.Element) -> Dict[str, str]:
        return {
            'groupId': getattr(dep.find('.//groupId'), 'text', None),
            'artifactId': getattr(dep.find('.//artifactId'), 'text', None),
            'version': getattr(dep.find('.//version'), 'text', None),
            'scope': getattr(dep.find('.//scope'), 'text', 'compile')
        }
    
    def _extract_dependency_list(self, root: ET.Element) -> List[Dict[str, str]]:
        return [self._extract_dependency(d) for d in root.findall('.//dependency')[:20]]
    
    def _extract_build_config(self, root: ET.Element) -> Dict[str, Any]:
        build = root.find('.//build')
        if build is None:
            return {}
        
        return {
            'sourceDirectory': getattr(build.find('.//sourceDirectory'), 'text', None),
            'outputDirectory': getattr(build.find('.//outputDirectory'), 'text', None),
            'finalName': getattr(build.find('.//finalName'), 'text', None)
        }
    
    def _calculate_pom_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        has_description = 1.0 if findings['project_info']['description'] else 0.0
        has_url = 1.0 if findings['project_info']['url'] else 0.0
        deps_with_version = sum(1 for d in findings['dependencies']['all'] if d.get('version'))
        total_deps = len(findings['dependencies']['all'])
        
        return {
            "completeness": (has_description + has_url) / 2,
            "dependency_management": deps_with_version / total_deps if total_deps > 0 else 1.0,
            "best_practices": 0.8 if findings['dependencies']['management'] > 0 else 0.4
        }

class Log4jConfigHandler(XMLHandler):
    """Handler for Log4j XML configuration files"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # Log4j 1.x uses 'log4j:configuration'
        if root.tag == 'log4j:configuration' or root.tag.endswith('}configuration'):
            if 'log4j' in root.tag:
                return True, 1.0
        # Log4j 2.x uses 'Configuration'
        if root.tag == 'Configuration':
            if root.find('.//Appenders') is not None or root.find('.//Loggers') is not None:
                return True, 0.9
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        version = "2.x" if root.tag == 'Configuration' else "1.x"
        
        return DocumentTypeInfo(
            type_name="Log4j Configuration",
            confidence=1.0,
            version=version,
            metadata={
                "framework": "Apache Log4j",
                "category": "logging_configuration"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        is_v2 = root.tag == 'Configuration'
        
        findings = {
            'version': "2.x" if is_v2 else "1.x",
            'appenders': self._analyze_appenders(root, is_v2),
            'loggers': self._analyze_loggers(root, is_v2),
            'log_levels': self._extract_log_levels(root, is_v2),
            'security_concerns': self._check_security_issues(root)
        }
        
        recommendations = [
            "Review log levels for production appropriateness",
            "Check for sensitive data in log patterns",
            "Ensure file appenders have proper rotation",
            "Validate external appender destinations"
        ]
        
        ai_use_cases = [
            "Log level optimization",
            "Security configuration analysis",
            "Performance impact assessment",
            "Compliance checking for log retention",
            "Sensitive data detection in patterns"
        ]
        
        return SpecializedAnalysis(
            document_type="Log4j Configuration",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={
                'appenders': len(findings['appenders']),
                'loggers': len(findings['loggers'])
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._assess_logging_quality(findings)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        is_v2 = root.tag == 'Configuration'
        
        return {
            'appender_configs': self._extract_appender_details(root, is_v2),
            'logger_configs': self._extract_logger_details(root, is_v2),
            'global_settings': self._extract_global_settings(root, is_v2)
        }
    
    def _analyze_appenders(self, root: ET.Element, is_v2: bool) -> List[Dict[str, Any]]:
        appenders = []
        
        if is_v2:
            for appender in root.findall('.//Appenders/*'):
                appenders.append({
                    'name': appender.get('name'),
                    'type': appender.tag,
                    'target': self._extract_v2_target(appender)
                })
        else:
            for appender in root.findall('.//appender'):
                appenders.append({
                    'name': appender.get('name'),
                    'class': appender.get('class'),
                    'type': self._extract_v1_type(appender.get('class', ''))
                })
        
        return appenders
    
    def _analyze_loggers(self, root: ET.Element, is_v2: bool) -> List[Dict[str, Any]]:
        loggers = []
        
        if is_v2:
            for logger in root.findall('.//Loggers/*'):
                loggers.append({
                    'name': logger.get('name', 'ROOT' if logger.tag == 'Root' else ''),
                    'level': logger.get('level'),
                    'additivity': logger.get('additivity', 'true')
                })
        else:
            for logger in root.findall('.//logger'):
                loggers.append({
                    'name': logger.get('name'),
                    'level': logger.find('.//level').get('value') if logger.find('.//level') is not None else None
                })
        
        return loggers
    
    def _extract_log_levels(self, root: ET.Element, is_v2: bool) -> Dict[str, int]:
        levels = {}
        
        if is_v2:
            for elem in root.findall('.//*[@level]'):
                level = elem.get('level').upper()
                levels[level] = levels.get(level, 0) + 1
        else:
            for level_elem in root.findall('.//level'):
                level = level_elem.get('value', '').upper()
                if level:
                    levels[level] = levels.get(level, 0) + 1
        
        return levels
    
    def _check_security_issues(self, root: ET.Element) -> List[str]:
        issues = []
        
        # Check for JNDI lookup patterns (Log4Shell vulnerability)
        for elem in root.iter():
            if elem.text and '${jndi:' in elem.text:
                issues.append("Potential JNDI lookup pattern detected")
        
        # Check for external socket appenders
        for appender in root.findall('.//appender'):
            if 'SocketAppender' in appender.get('class', ''):
                issues.append("External socket appender detected")
        
        return issues
    
    def _extract_v2_target(self, appender: ET.Element) -> Optional[str]:
        if appender.tag == 'File':
            return appender.get('fileName')
        elif appender.tag == 'Console':
            return appender.get('target', 'SYSTEM_OUT')
        return None
    
    def _extract_v1_type(self, class_name: str) -> str:
        if 'ConsoleAppender' in class_name:
            return 'Console'
        elif 'FileAppender' in class_name:
            return 'File'
        elif 'RollingFileAppender' in class_name:
            return 'RollingFile'
        return 'Other'
    
    def _extract_appender_details(self, root: ET.Element, is_v2: bool) -> List[Dict[str, Any]]:
        # Detailed implementation would extract full appender configurations
        return self._analyze_appenders(root, is_v2)
    
    def _extract_logger_details(self, root: ET.Element, is_v2: bool) -> List[Dict[str, Any]]:
        # Detailed implementation would extract full logger configurations
        return self._analyze_loggers(root, is_v2)
    
    def _extract_global_settings(self, root: ET.Element, is_v2: bool) -> Dict[str, Any]:
        settings = {}
        
        if is_v2:
            settings['status'] = root.get('status', 'ERROR')
            settings['monitorInterval'] = root.get('monitorInterval')
        else:
            settings['threshold'] = root.get('threshold')
            settings['debug'] = root.get('debug', 'false')
        
        return settings
    
    def _assess_logging_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        # Check for good practices
        has_file_rotation = any('Rolling' in a.get('type', '') for a in findings['appenders'])
        has_appropriate_levels = 'DEBUG' not in findings['log_levels'] or findings['log_levels'].get('DEBUG', 0) < 5
        no_security_issues = len(findings['security_concerns']) == 0
        
        return {
            "security": 1.0 if no_security_issues else 0.3,
            "production_ready": 1.0 if has_appropriate_levels else 0.5,
            "reliability": 1.0 if has_file_rotation else 0.6
        }

class SpringConfigHandler(XMLHandler):
    """Handler for Spring Framework XML configuration files"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # Check for Spring namespaces
        spring_indicators = [
            'springframework.org/schema/beans',
            'springframework.org/schema/context',
            'springframework.org/schema/mvc'
        ]
        
        if any(ind in str(namespaces.values()) for ind in spring_indicators):
            return True, 1.0
        
        # Check for beans root element
        if root.tag == 'beans' or root.tag.endswith('}beans'):
            return True, 0.7
        
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        # Detect Spring version from schema
        version = "5.x"  # Default
        for uri in namespaces.values():
            if 'springframework.org/schema' in uri:
                version_match = re.search(r'/(\d+\.\d+)\.xsd', uri)
                if version_match:
                    version = version_match.group(1)
                    break
        
        return DocumentTypeInfo(
            type_name="Spring Configuration",
            confidence=1.0,
            version=version,
            metadata={
                "framework": "Spring Framework",
                "category": "dependency_injection"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            'beans': self._analyze_beans(root),
            'profiles': self._extract_profiles(root),
            'imports': self._extract_imports(root),
            'property_sources': self._extract_property_sources(root),
            'aop_config': self._check_aop_usage(root),
            'security_config': self._check_security_config(root)
        }
        
        recommendations = [
            "Review bean dependencies for circular references",
            "Check for hardcoded values that should be externalized",
            "Validate security configurations",
            "Consider migrating to annotation-based config"
        ]
        
        ai_use_cases = [
            "Dependency graph visualization",
            "Security misconfiguration detection",
            "Migration to modern Spring Boot",
            "Configuration optimization",
            "Circular dependency detection"
        ]
        
        return SpecializedAnalysis(
            document_type="Spring Configuration",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={
                'beans': len(findings['beans']['all']),
                'profiles': len(findings['profiles']),
                'property_sources': len(findings['property_sources'])
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._assess_spring_config_quality(findings)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'bean_definitions': self._extract_bean_definitions(root),
            'component_scans': self._extract_component_scans(root),
            'configurations': self._extract_configurations(root)
        }
    
    def _analyze_beans(self, root: ET.Element, namespaces: Dict[str, str] = None) -> Dict[str, Any]:
        beans = []
        bean_classes = {}
        
        for bean in root.findall('.//*[@id]'):
            if bean.tag.endswith('bean') or bean.tag == 'bean':
                bean_info = {
                    'id': bean.get('id'),
                    'class': bean.get('class'),
                    'scope': bean.get('scope', 'singleton'),
                    'lazy': bean.get('lazy-init', 'false'),
                    'parent': bean.get('parent')
                }
                beans.append(bean_info)
                
                # Count bean classes
                if bean_info['class']:
                    bean_classes[bean_info['class']] = bean_classes.get(bean_info['class'], 0) + 1
        
        return {
            'all': beans,
            'count': len(beans),
            'by_scope': self._count_by_attribute(beans, 'scope'),
            'lazy_count': sum(1 for b in beans if b['lazy'] == 'true'),
            'common_classes': {k: v for k, v in bean_classes.items() if v > 1}
        }
    
    def _extract_profiles(self, root: ET.Element) -> List[str]:
        profiles = set()
        
        for elem in root.findall('.//*[@profile]'):
            profile = elem.get('profile')
            if profile:
                # Handle multiple profiles
                for p in profile.split(','):
                    profiles.add(p.strip())
        
        return list(profiles)
    
    def _extract_imports(self, root: ET.Element) -> List[str]:
        imports = []
        
        for imp in root.findall('.//import'):
            resource = imp.get('resource')
            if resource:
                imports.append(resource)
        
        return imports
    
    def _extract_property_sources(self, root: ET.Element) -> List[Dict[str, str]]:
        sources = []
        
        # Look for property placeholder configurers
        for elem in root.findall('.//*'):
            if 'PropertyPlaceholderConfigurer' in elem.get('class', ''):
                location = elem.find('.//property[@name="location"]')
                if location is not None:
                    sources.append({
                        'type': 'properties',
                        'location': location.get('value')
                    })
        
        return sources
    
    def _check_aop_usage(self, root: ET.Element) -> bool:
        # Check for AOP namespace or AOP-related beans
        for elem in root.iter():
            if 'aop' in elem.tag or 'aspectj' in elem.tag.lower():
                return True
        return False
    
    def _check_security_config(self, root: ET.Element) -> Dict[str, Any]:
        security = {
            'present': False,
            'authentication': False,
            'authorization': False
        }
        
        for elem in root.iter():
            if 'security' in elem.tag:
                security['present'] = True
            if 'authentication' in elem.tag:
                security['authentication'] = True
            if 'authorization' in elem.tag or 'access' in elem.tag:
                security['authorization'] = True
        
        return security
    
    def _extract_bean_definitions(self, root: ET.Element) -> List[Dict[str, Any]]:
        # Simplified version - full implementation would extract all properties
        return self._analyze_beans(root)['all'][:20]  # First 20 beans
    
    def _extract_component_scans(self, root: ET.Element) -> List[str]:
        scans = []
        
        for scan in root.findall('.//*component-scan'):
            base_package = scan.get('base-package')
            if base_package:
                scans.append(base_package)
        
        return scans
    
    def _extract_configurations(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'transaction_management': self._check_transaction_config(root),
            'caching': self._check_cache_config(root),
            'scheduling': self._check_scheduling_config(root)
        }
    
    def _check_transaction_config(self, root: ET.Element) -> bool:
        return any('transaction' in elem.tag for elem in root.iter())
    
    def _check_cache_config(self, root: ET.Element) -> bool:
        return any('cache' in elem.tag for elem in root.iter())
    
    def _check_scheduling_config(self, root: ET.Element) -> bool:
        return any('task' in elem.tag or 'scheduling' in elem.tag for elem in root.iter())
    
    def _count_by_attribute(self, items: List[Dict], attr: str) -> Dict[str, int]:
        counts = {}
        for item in items:
            value = item.get(attr)
            if value:
                counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _assess_spring_config_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        # Assess configuration quality
        beans = findings['beans']
        
        # Check for good practices
        uses_profiles = len(findings['profiles']) > 0
        externalizes_config = len(findings['property_sources']) > 0
        reasonable_bean_count = beans['count'] < 100  # Large XML configs are hard to maintain
        
        return {
            "maintainability": 0.8 if reasonable_bean_count else 0.3,
            "flexibility": 1.0 if uses_profiles else 0.5,
            "configuration_management": 1.0 if externalizes_config else 0.4
        }

class DocBookHandler(XMLHandler):
    """Handler for DocBook XML documentation files"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # Check for DocBook elements
        docbook_roots = ['book', 'article', 'chapter', 'section', 'para']
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        
        if tag in docbook_roots:
            return True, 0.8
        
        # Check for DocBook namespace
        if any('docbook.org' in uri for uri in namespaces.values()):
            return True, 1.0
        
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        
        return DocumentTypeInfo(
            type_name="DocBook Documentation",
            confidence=0.9,
            version="5.0",  # Assume 5.0 unless specified
            metadata={
                "document_type": tag,
                "category": "technical_documentation"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        findings = {
            'structure': self._analyze_document_structure(root),
            'metadata': self._extract_metadata(root),
            'content_stats': self._analyze_content(root),
            'media': self._find_media_references(root),
            'cross_references': self._find_cross_references(root)
        }
        
        recommendations = [
            "Extract for documentation search system",
            "Generate multiple output formats (HTML, PDF)",
            "Check for broken cross-references",
            "Analyze readability and completeness"
        ]
        
        ai_use_cases = [
            "Documentation quality analysis",
            "Automatic summary generation",
            "Technical content extraction",
            "Glossary and index generation",
            "Documentation translation"
        ]
        
        return SpecializedAnalysis(
            document_type="DocBook Documentation",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={
                'chapters': len(findings['structure']['chapters']),
                'sections': findings['structure']['total_sections'],
                'media_items': len(findings['media'])
            },
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._assess_documentation_quality(findings)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'title': self._extract_title(root),
            'table_of_contents': self._generate_toc(root),
            'glossary': self._extract_glossary(root),
            'code_examples': self._extract_code_examples(root)
        }
    
    def _analyze_document_structure(self, root: ET.Element) -> Dict[str, Any]:
        structure = {
            'type': root.tag.split('}')[-1] if '}' in root.tag else root.tag,
            'chapters': [],
            'total_sections': 0,
            'max_depth': 0
        }
        
        # Find chapters
        for chapter in root.findall('.//chapter'):
            title_elem = chapter.find('.//title')
            structure['chapters'].append({
                'title': title_elem.text if title_elem is not None else 'Untitled',
                'sections': len(chapter.findall('.//section'))
            })
        
        # Count all sections
        structure['total_sections'] = len(root.findall('.//section'))
        
        return structure
    
    def _extract_metadata(self, root: ET.Element) -> Dict[str, Any]:
        info = root.find('.//info') or root.find('.//bookinfo') or root.find('.//articleinfo')
        
        if info is None:
            return {}
        
        return {
            'title': getattr(info.find('.//title'), 'text', None),
            'author': self._extract_author(info),
            'date': getattr(info.find('.//date'), 'text', None),
            'abstract': getattr(info.find('.//abstract'), 'text', None)
        }
    
    def _analyze_content(self, root: ET.Element) -> Dict[str, Any]:
        return {
            'paragraphs': len(root.findall('.//para')),
            'lists': len(root.findall('.//itemizedlist')) + len(root.findall('.//orderedlist')),
            'tables': len(root.findall('.//table')),
            'examples': len(root.findall('.//example')),
            'notes': len(root.findall('.//note')),
            'warnings': len(root.findall('.//warning'))
        }
    
    def _find_media_references(self, root: ET.Element) -> List[Dict[str, str]]:
        media = []
        
        for elem in root.findall('.//imagedata'):
            media.append({
                'type': 'image',
                'fileref': elem.get('fileref'),
                'format': elem.get('format')
            })
        
        return media
    
    def _find_cross_references(self, root: ET.Element) -> List[str]:
        xrefs = []
        
        for xref in root.findall('.//xref'):
            linkend = xref.get('linkend')
            if linkend:
                xrefs.append(linkend)
        
        return xrefs
    
    def _extract_title(self, root: ET.Element) -> str:
        title = root.find('.//title')
        return title.text if title is not None else 'Untitled'
    
    def _generate_toc(self, root: ET.Element) -> List[Dict[str, Any]]:
        toc = []
        
        for chapter in root.findall('.//chapter'):
            chapter_title = chapter.find('.//title')
            if chapter_title is not None:
                toc_entry = {
                    'title': chapter_title.text,
                    'sections': []
                }
                
                for section in chapter.findall('.//section'):
                    section_title = section.find('.//title')
                    if section_title is not None:
                        toc_entry['sections'].append(section_title.text)
                
                toc.append(toc_entry)
        
        return toc
    
    def _extract_glossary(self, root: ET.Element) -> List[Dict[str, str]]:
        glossary = []
        
        for entry in root.findall('.//glossentry'):
            term = entry.find('.//glossterm')
            definition = entry.find('.//glossdef')
            
            if term is not None and definition is not None:
                glossary.append({
                    'term': term.text,
                    'definition': definition.text
                })
        
        return glossary
    
    def _extract_code_examples(self, root: ET.Element) -> List[Dict[str, str]]:
        examples = []
        
        for example in root.findall('.//programlisting'):
            examples.append({
                'language': example.get('language', 'unknown'),
                'code': example.text if example.text else ''
            })
        
        return examples[:10]  # First 10 examples
    
    def _extract_author(self, info: ET.Element) -> Optional[str]:
        author = info.find('.//author')
        if author is not None:
            firstname = author.find('.//firstname')
            surname = author.find('.//surname')
            if firstname is not None and surname is not None:
                return f"{firstname.text} {surname.text}"
        return None
    
    def _assess_documentation_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        content = findings['content_stats']
        
        # Check for good documentation practices
        has_examples = content['examples'] > 0
        has_structure = findings['structure']['total_sections'] > 0
        has_metadata = bool(findings['metadata'])
        
        # Calculate ratios
        example_ratio = min(content['examples'] / max(findings['structure']['total_sections'], 1), 1.0)
        warning_ratio = content['warnings'] / max(content['paragraphs'], 1)
        
        return {
            "completeness": (has_examples + has_structure + has_metadata) / 3,
            "example_coverage": example_ratio,
            "safety_documentation": min(warning_ratio * 10, 1.0)  # Good to have some warnings
        }

class SitemapHandler(XMLHandler):
    """Handler for XML sitemap files"""
    
    def can_handle(self, root: ET.Element, namespaces: Dict[str, str]) -> Tuple[bool, float]:
        # Check for sitemap namespace
        if 'sitemaps.org/schemas/sitemap' in str(namespaces.values()):
            return True, 1.0
        
        # Check for urlset or sitemapindex root
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        if tag in ['urlset', 'sitemapindex']:
            return True, 0.8
        
        return False, 0.0
    
    def detect_type(self, root: ET.Element, namespaces: Dict[str, str]) -> DocumentTypeInfo:
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        is_index = tag == 'sitemapindex'
        
        return DocumentTypeInfo(
            type_name="XML Sitemap" + (" Index" if is_index else ""),
            confidence=1.0,
            version="0.9",
            schema_uri="http://www.sitemaps.org/schemas/sitemap/0.9",
            metadata={
                "type": "sitemap_index" if is_index else "url_sitemap",
                "category": "seo"
            }
        )
    
    def analyze(self, root: ET.Element, file_path: str) -> SpecializedAnalysis:
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        is_index = tag == 'sitemapindex'
        
        if is_index:
            findings = self._analyze_sitemap_index(root)
        else:
            findings = self._analyze_url_sitemap(root)
        
        recommendations = [
            "Validate URLs for accessibility",
            "Check for outdated or broken links",
            "Analyze URL patterns for SEO optimization",
            "Monitor change frequencies vs actual updates"
        ]
        
        ai_use_cases = [
            "SEO health monitoring",
            "Content update pattern analysis",
            "Website structure visualization",
            "Broken link detection",
            "Content priority optimization"
        ]
        
        return SpecializedAnalysis(
            document_type="XML Sitemap",
            key_findings=findings,
            recommendations=recommendations,
            data_inventory={'urls': findings.get('url_count', 0)},
            ai_use_cases=ai_use_cases,
            structured_data=self.extract_key_data(root),
            quality_metrics=self._assess_sitemap_quality(findings)
        )
    
    def extract_key_data(self, root: ET.Element) -> Dict[str, Any]:
        tag = root.tag.split('}')[-1] if '}' in root.tag else root.tag
        
        if tag == 'sitemapindex':
            return {
                'sitemaps': self._extract_sitemaps(root)
            }
        else:
            return {
                'urls': self._extract_urls(root)[:100]  # First 100 URLs
            }
    
    def _analyze_url_sitemap(self, root: ET.Element) -> Dict[str, Any]:
        urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
        
        findings = {
            'url_count': len(urls),
            'priorities': self._analyze_priorities(urls),
            'change_frequencies': self._analyze_changefreqs(urls),
            'last_modified': self._analyze_lastmod(urls),
            'url_patterns': self._analyze_url_patterns(urls)
        }
        
        return findings
    
    def _analyze_sitemap_index(self, root: ET.Element) -> Dict[str, Any]:
        sitemaps = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
        
        findings = {
            'sitemap_count': len(sitemaps),
            'last_modified': self._analyze_sitemap_dates(sitemaps)
        }
        
        return findings
    
    def _analyze_priorities(self, urls: List[ET.Element]) -> Dict[str, int]:
        priorities = {}
        
        for url in urls:
            priority = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
            if priority is not None and priority.text:
                p_value = priority.text
                priorities[p_value] = priorities.get(p_value, 0) + 1
        
        return priorities
    
    def _analyze_changefreqs(self, urls: List[ET.Element]) -> Dict[str, int]:
        frequencies = {}
        
        for url in urls:
            changefreq = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
            if changefreq is not None and changefreq.text:
                freq = changefreq.text
                frequencies[freq] = frequencies.get(freq, 0) + 1
        
        return frequencies
    
    def _analyze_lastmod(self, urls: List[ET.Element]) -> Dict[str, Any]:
        dates = []
        
        for url in urls:
            lastmod = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if lastmod is not None and lastmod.text:
                dates.append(lastmod.text)
        
        if dates:
            return {
                'count': len(dates),
                'latest': max(dates),
                'oldest': min(dates)
            }
        
        return {'count': 0}
    
    def _analyze_url_patterns(self, urls: List[ET.Element]) -> Dict[str, Any]:
        patterns = {
            'domains': set(),
            'extensions': {},
            'depth_levels': {}
        }
        
        for url in urls[:1000]:  # Analyze first 1000 URLs
            loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc is not None and loc.text:
                url_text = loc.text
                
                # Extract domain
                if '://' in url_text:
                    domain = url_text.split('://')[1].split('/')[0]
                    patterns['domains'].add(domain)
                
                # Count depth
                depth = url_text.count('/') - 2  # Subtract protocol slashes
                patterns['depth_levels'][depth] = patterns['depth_levels'].get(depth, 0) + 1
        
        patterns['domains'] = list(patterns['domains'])
        return patterns
    
    def _analyze_sitemap_dates(self, sitemaps: List[ET.Element]) -> Dict[str, Any]:
        dates = []
        
        for sitemap in sitemaps:
            lastmod = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if lastmod is not None and lastmod.text:
                dates.append(lastmod.text)
        
        if dates:
            return {
                'latest': max(dates),
                'oldest': min(dates)
            }
        
        return {}
    
    def _extract_urls(self, root: ET.Element) -> List[Dict[str, str]]:
        urls = []
        
        for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            url_data = {}
            
            loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc is not None:
                url_data['loc'] = loc.text
            
            lastmod = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if lastmod is not None:
                url_data['lastmod'] = lastmod.text
            
            changefreq = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}changefreq')
            if changefreq is not None:
                url_data['changefreq'] = changefreq.text
            
            priority = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
            if priority is not None:
                url_data['priority'] = priority.text
            
            urls.append(url_data)
        
        return urls
    
    def _extract_sitemaps(self, root: ET.Element) -> List[Dict[str, str]]:
        sitemaps = []
        
        for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
            sitemap_data = {}
            
            loc = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
            if loc is not None:
                sitemap_data['loc'] = loc.text
            
            lastmod = sitemap.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
            if lastmod is not None:
                sitemap_data['lastmod'] = lastmod.text
            
            sitemaps.append(sitemap_data)
        
        return sitemaps
    
    def _assess_sitemap_quality(self, findings: Dict[str, Any]) -> Dict[str, float]:
        quality = {}
        
        # Check if URLs have recommended attributes
        url_count = findings.get('url_count', 0)
        if url_count > 0:
            has_priority = sum(findings.get('priorities', {}).values())
            has_changefreq = sum(findings.get('change_frequencies', {}).values())
            has_lastmod = findings.get('last_modified', {}).get('count', 0)
            
            quality['completeness'] = (
                (has_priority / url_count * 0.3) +
                (has_changefreq / url_count * 0.3) +
                (has_lastmod / url_count * 0.4)
            )
        else:
            quality['completeness'] = 0.0
        
        # Check URL diversity
        if 'url_patterns' in findings:
            depth_distribution = len(findings['url_patterns'].get('depth_levels', {}))
            quality['structure_diversity'] = min(depth_distribution / 5.0, 1.0)
        
        return quality

# Additional handler classes can be added here:
# - WSDLHandler (for web service definitions)
# - XSLTHandler (for transformation stylesheets)
# - KMLHandler (for geographic data)
# - XMLSchemaHandler (for XSD files)
# - Ant/NantBuildHandler (for build scripts)
# - NuGetHandler (for .nuspec files)
# - etc.
