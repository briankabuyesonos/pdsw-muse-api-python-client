import xml.etree.ElementTree as Reader
import glob
from common import get_muse_source


class MuseXmlParser(object):
    """
    Helper class for reading and formatting the xmls
    """
    def __init__(self, args):
        """
        :param args: GeneratorParser args
        """
        xml_dir, self.muse_release_version = get_muse_source(args)
        self.xml = self.read_spec('muse-namespace', xml_dir)
        self.xml_types = self.read_spec('dataType',xml_dir+'/types')
        self.xml_enums = self.read_spec('enum', xml_dir+'/enums')


    # File helpers
    def write_file(self, filepath, contents):
        f = open(filepath, 'w')
        f.write(contents)
        f.close()

    def read_file(self, filepath):
        return open(filepath, 'r').read()

    def read_spec(self, definition_tag, filepath=None):
        """
        Load the XMLs from filepath
        :param definition_tag: xml tag name
        :param filepath:
        :return:
        """

        # Read the given xml files
        xml_directory = filepath if filepath.endswith("/") else filepath + "/"
        api_definitions = [Reader.parse(xml).getroot() for xml in glob.glob(xml_directory + "*.xml")]
        api_definitions = [api_definition for api_definition in api_definitions
                           if api_definition.tag == definition_tag]
        api_definitions.sort(key=lambda xml: xml.attrib["name"])
        return api_definitions

    def read_spec_for_dataTypes(self, filepath=None):
        """
        Load the XMLs from file for custom dataTypes
        :param filepath:
        :return:
        """

        # Read the given xml/type files
        xml_type_directory = filepath if filepath.endswith("/") else filepath + "/"
        dataType_definitions = [Reader.parse(xml).getroot() for xml in glob.glob(xml_type_directory + "*.xml")]
        dataType_definitions = [dataType_definition for dataType_definition in dataType_definitions
                           if dataType_definition.tag == "dataType"]

        dataType_definitions.sort(key=lambda xml: xml.attrib["name"])
        return dataType_definitions

