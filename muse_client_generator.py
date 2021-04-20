import pystache
from mustache.muse_client_view import MuseRestClient, MuseWebsocketClient, MuseEvents, MuseEventEnums
from xml_parser import MuseXmlParser
from common import GeneratorParser


# Read command line options
cl_parser = GeneratorParser(description='Generate a muse rest client from muse xml definitions.',
                            default_output_dir="sonos_museclient")
args = cl_parser.parse_args()
output_path = args.output_dir if args.output_dir.endswith("/") else args.output_dir + "/"

# region Renderer
renderer = pystache.Renderer()

# Pulls the xmls from the muse git repo and reads them into memory
xml_parser = MuseXmlParser(args)

print "\n------------------------------\n\nRendering Muse v1 REST client..."
rest_client_view_v1 = MuseRestClient(api_version='1', parser=xml_parser)
xml_parser.write_file(output_path + "muse_rest_client.py", "# muse_release_version: {}".format(
    xml_parser.muse_release_version)+"\n"+renderer.render(rest_client_view_v1))
print "\n------------------------------\n\nRendering Muse v2 REST client..."
rest_client_view_v2 = MuseRestClient(api_version='2', parser=xml_parser)
xml_parser.write_file(output_path + "muse_rest_client_v2.py", "# muse_release_version: {}".format(
    xml_parser.muse_release_version)+"\n"+renderer.render(rest_client_view_v2))

print "\n------------------------------\n\nRendering Muse v1 websocket client..."
websocket_client_view_v1 = MuseWebsocketClient(api_version='1', parser=xml_parser)
xml_parser.write_file(output_path + "muse_websocket_client.py", "# muse_release_version: {}".format(
    xml_parser.muse_release_version)+"\n"+renderer.render(websocket_client_view_v1))
print "\n------------------------------\n\nRendering Muse v2 websocket client..."
websocket_client_view_v2 = MuseWebsocketClient(api_version='2', parser=xml_parser)
xml_parser.write_file(output_path + "muse_websocket_client_v2.py", "# muse_release_version: {}".format(
    xml_parser.muse_release_version)+"\n"+renderer.render(websocket_client_view_v2))

print "\n------------------------------\n\nRendering event classes..."
event_client_view = MuseEvents(xml_parser)
xml_parser.write_file(output_path + "muse_events.py", "# muse_release_version: {}".format(
    xml_parser.muse_release_version)+"\n"+renderer.render(event_client_view))

print "\n------------------------------\n\nRendering enum classes..."
enums_client_view = MuseEventEnums(xml_parser)
xml_parser.write_file(output_path + "muse_event_enums.py", "# muse_release_version: {}".format(
    xml_parser.muse_release_version)+"\n"+renderer.render(enums_client_view))

print "\n------------------------------\n\nDone!"
# endregion
