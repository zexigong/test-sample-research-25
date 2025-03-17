import pytest
import xml.dom.minidom
from pyinstaller.test_winmanifest.test_winmanifest import (
    _find_elements_by_tag,
    _find_element_by_tag,
    _set_execution_level,
    _ensure_common_controls_dependency,
    create_application_manifest,
    write_manifest_to_executable,
    read_manifest_from_executable,
    _DEFAULT_MANIFEST_XML
)
from unittest import mock

def test_find_elements_by_tag():
    xml_str = b"""<root><tag1/><tag2/><tag1/></root>"""
    dom = xml.dom.minidom.parseString(xml_str)
    root = dom.documentElement
    elements = _find_elements_by_tag(root, "tag1")
    assert len(elements) == 2
    assert all(el.tagName == "tag1" for el in elements)

def test_find_element_by_tag_single():
    xml_str = b"""<root><tag1/><tag2/></root>"""
    dom = xml.dom.minidom.parseString(xml_str)
    root = dom.documentElement
    element = _find_element_by_tag(root, "tag1")
    assert element is not None
    assert element.tagName == "tag1"

def test_find_element_by_tag_none():
    xml_str = b"""<root><tag2/></root>"""
    dom = xml.dom.minidom.parseString(xml_str)
    root = dom.documentElement
    element = _find_element_by_tag(root, "tag1")
    assert element is None

def test_find_element_by_tag_multiple():
    xml_str = b"""<root><tag1/><tag1/></root>"""
    dom = xml.dom.minidom.parseString(xml_str)
    root = dom.documentElement
    with pytest.raises(ValueError):
        _find_element_by_tag(root, "tag1")

def test_set_execution_level():
    xml_str = b"""<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"></assembly>"""
    dom = xml.dom.minidom.parseString(xml_str)
    root = dom.documentElement
    _set_execution_level(dom, root, uac_admin=True, uac_uiaccess=True)
    requested_execution_level = _find_element_by_tag(
        _find_element_by_tag(
            _find_element_by_tag(
                _find_element_by_tag(root, "trustInfo"), "security"
            ),
            "requestedPrivileges"
        ),
        "requestedExecutionLevel"
    )
    assert requested_execution_level.getAttribute("level") == "requireAdministrator"
    assert requested_execution_level.getAttribute("uiAccess") == "true"

def test_ensure_common_controls_dependency():
    xml_str = b"""<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"></assembly>"""
    dom = xml.dom.minidom.parseString(xml_str)
    root = dom.documentElement
    _ensure_common_controls_dependency(dom, root)
    dependency = _find_element_by_tag(root, "dependency")
    assert dependency is not None
    dependent_assembly = _find_element_by_tag(dependency, "dependentAssembly")
    assert dependent_assembly is not None
    assembly_identity = _find_element_by_tag(dependent_assembly, "assemblyIdentity")
    assert assembly_identity is not None
    assert assembly_identity.getAttribute("name") == "Microsoft.Windows.Common-Controls"

def test_create_application_manifest_default():
    manifest = create_application_manifest()
    dom = xml.dom.minidom.parseString(manifest)
    root = dom.documentElement
    assert root.tagName == "assembly"
    assert root.getAttribute("manifestVersion") == "1.0"
    assert _find_element_by_tag(root, "trustInfo") is not None

def test_create_application_manifest_custom():
    custom_manifest = b"""<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0"></assembly>"""
    manifest = create_application_manifest(manifest_xml=custom_manifest, uac_admin=True)
    dom = xml.dom.minidom.parseString(manifest)
    root = dom.documentElement
    requested_execution_level = _find_element_by_tag(
        _find_element_by_tag(
            _find_element_by_tag(
                _find_element_by_tag(root, "trustInfo"), "security"
            ),
            "requestedPrivileges"
        ),
        "requestedExecutionLevel"
    )
    assert requested_execution_level.getAttribute("level") == "requireAdministrator"

@mock.patch('pyinstaller.test_winmanifest.test_winmanifest.write_manifest_to_executable')
def test_write_manifest_to_executable(mock_write_manifest):
    filename = "dummy_executable.exe"
    manifest_xml = _DEFAULT_MANIFEST_XML
    write_manifest_to_executable(filename, manifest_xml)
    mock_write_manifest.assert_called_once_with(filename, manifest_xml)

@mock.patch('pyinstaller.test_winmanifest.test_winmanifest.read_manifest_from_executable')
def test_read_manifest_from_executable(mock_read_manifest):
    filename = "dummy_executable.exe"
    mock_read_manifest.return_value = _DEFAULT_MANIFEST_XML
    manifest_xml = read_manifest_from_executable(filename)
    mock_read_manifest.assert_called_once_with(filename)
    assert manifest_xml == _DEFAULT_MANIFEST_XML