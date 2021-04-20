import re
import keyword


def should_include(api_version, component):
    """
    Do some loose filtering based on the api major version.
    Only return true if the component is between the sinceVersion and/or removedVersion
    depending on which one is defined for a given api component.
    :param api_version:
    :param component:
    :return:
    """
    # Get the major version value only
    try:
        component_since_version_major = component.get("sinceVersion").split(".")[0]
    except:
        component_since_version_major = None
    try:
        component_removed_version_major = component.get("removedVersion").split(".")[0]
    except:
        component_removed_version_major = None

    if component_since_version_major is not None and component_removed_version_major is not None:
        if component_since_version_major <= api_version < component_removed_version_major:
            return True
    elif component_since_version_major is not None and component_removed_version_major is None:
        if component_since_version_major <= api_version:
            return True
    elif component_since_version_major is None and component_removed_version_major is not None:
        if api_version < component_removed_version_major:
            return True
    else:
        return True

    return False


class BaseMuseClientView(object):
    def __init__(self, parser, is_rest_client=False, api_version="1"):
        """
        Base view class for muse clients

        :param parser:
        :param is_rest_client: Rest clients will filter out the "subscribe" commands since they are not applicable.
        :param api_version: Specify the muse version to use
        """
        self.parser = parser
        self.is_rest_client = is_rest_client
        self.api_version = api_version

    # region XML Formatting Helpers
    def _clean_description(self, description, default=""):
        if description is not None:
            text = description.text.encode('ascii', errors="ignore")
            return text.strip().strip("\n").rstrip("\n").replace("&quot;", '"')
        else:
            return default

    def init(self):
        """
        Formatting for the muse rest client init section
        :return:
        """
        values = {}

        if self.api_version == "1":
            values["pass_apiKey"] = True
            values["init_apiKey"] = True
        if self.is_rest_client:
            values["apiVersion"] = str(self.api_version)

        return values

    def namespaces(self):
        """
        List of namespaces
        :return:
        """
        namespace_names = []
        # Filter out namespace objects based on its sinceVersion and/or removedVersion
        self.parser.xml = filter(lambda x: should_include(api_version=self.api_version,
                                                          component=x),
                                 self.parser.xml)
        for xml in self.parser.xml:
            name = xml.attrib["name"]
            # The "global" namespace name causes issues since "global" is a reserved python keyword
            values = {
                "var_name": name if name != "global" else "global_ns",
                "namespace_name": name
            }
            if self.api_version == "1":
                values["pass_apiKey"] = True
            namespace_names.append(values)

        return namespace_names

    def clients(self):
        namespaces = []
        # Filter out namespace objects based on its sinceVersion and/or removedVersion
        self.parser.xml = filter(lambda x: should_include(api_version=self.api_version,
                                                          component=x),
                                 self.parser.xml)
        for namespace_definition in self.parser.xml:
            # Build the mustache view object
            namespace = {
                "namespace_name": namespace_definition.attrib["name"],
                "namespace_description": self._clean_description(namespace_definition.find('description'),
                                                                 ""),
                "commands": []
            }

            # Pull out commmands
            namespace["commands"] = self._build_commands(namespace_definition.find("commands").findall("command"),
                                                         namespace=namespace["namespace_name"],
                                                         namespace_target=namespace_definition.attrib["target"])

            namespaces.append(namespace)

        return namespaces

    def _build_commands(self, command_definitions, namespace, namespace_target):
        commands = []

        if self.is_rest_client:
            # Filter out subscribe because it is pointless
            if "upnp" not in namespace:
                command_definitions = [c for c in command_definitions if "subscribe" not in c.attrib["name"]]
            # Filter out command objects based on its sinceVersion and/or removedVersion
            command_definitions = filter(lambda cmd: should_include(api_version=self.api_version,
                                                                    component=cmd),
                                         command_definitions)

        for command_definition in command_definitions:
            # Build the mustache view object
            command = {
                "command_name": command_definition.attrib["name"],
                "command_description": self._clean_description(command_definition.find('description')),
                "rest_method": command_definition.attrib.get("restMethod", "POST"),
                "namespace": namespace,
                "resource_id": command_definition.attrib.get("resourceId", "")
            }

            target = command_definition.attrib.get("target", namespace_target)
            scope = command_definition.attrib.get("scope", "")

            # Format parameters for target
            target_args = ["sid"] if target == "sessionId" else []

            # Format command-specific parameters
            # Can be defined in 3 ways:
            # 1. non custom dataTypes - in-line definitions
            # 2. custom dataTypes - defined in:
            #   a. dataTypes attribute within the same namespace.xml
            #   b. dataType attribute in dataType.xml located in directory muse_platform_api/xml/types
            required_args, optional_args = self._get_command_parameters(command_definition, namespace)
            command["required_args"] = target_args + [p.attrib["name"] for p in required_args]
            command["optional_args"] = [p.attrib["name"] for p in optional_args]

            required_args_map = [{"name": param.attrib.get("name"), "isReserved": param.attrib.get("isReserved")}
                                 for param in required_args]
            optional_args_map = [{"name": param.attrib.get("name"), "isReserved": param.attrib.get("isReserved")}
                                 for param in optional_args]
            command["required_args_map"] = required_args_map
            command["optional_args_map"] = optional_args_map

            if len(target_args) > 0:
                for arg in target_args:
                    command["required_args_map"].append({"name": arg, "isReserved": False})

            # Hack workaround for the GET'er of restricted settings
            # You have to add the setting to the end of the rest path, which is not defined in the source xml
            if command["command_name"] == "getRestrictedAdminSettings":
                command["resource_id"] = "setting"
                command["required_args"].append("setting")
                command["required_args_map"].append({"name": "setting", "isReserved": False})

            # Create the header arguments for the target
            if target and target != "none":
                command["headers"] = [self._build_headers(target)]

            # Required body values (minus resource_id and session id, which are in the path)
            req_body_params = [p for p in command["required_args"] if p != "sid"]
            req_body_params_map = [{"name": param.attrib.get("name"), "isReserved": param.attrib.get("isReserved")}
                                   for param in required_args if param.attrib.get("name") != "sid"]
            if command["command_name"] == "getRestrictedAdminSettings":
                req_body_params_map.append({"name": "setting", "isReserved": False})

            # Missing body values (minus session id, which is in the path)
            missing_body_params = req_body_params

            if self.is_rest_client:
                # For rest commands, the resource id is already in the path. For websocket, it should stay in the header
                req_body_params = [p for p in req_body_params if p != command["resource_id"]]
                req_body_params_map = [{"name": param.attrib.get("name"), "isReserved": param.attrib.get("isReserved")}
                                       for param in required_args if param.attrib.get("name") != command["resource_id"]]

            if len(missing_body_params) > 0:
                command["missing_body"] = {
                    "missing_body_params": missing_body_params
                }

            if len(req_body_params) > 0:
                command["req_body"] = {
                    "req_body_params": req_body_params,
                    "req_body_params_map": req_body_params_map
                }

            # Optional body values (minus resource_id, which is in the path for REST)
            if self.is_rest_client:
                opt_body_params = [p for p in command["optional_args"] if p != command["resource_id"]]
                opt_body_params_map = [{"name": param.attrib.get("name"), "isReserved": param.attrib.get("isReserved")}
                                       for param in optional_args if param.attrib.get("name") != command["resource_id"]]
            else:
                opt_body_params = command["optional_args"]
                opt_body_params_map = [{"name": param.attrib.get("name"), "isReserved": param.attrib.get("isReserved")}
                                       for param in optional_args]
            if len(opt_body_params) > 0:
                command["opt_body"] = {
                    "opt_body_params": opt_body_params,
                    "opt_body_params_map": opt_body_params_map
                }

            command["api_version"] = self.api_version

            # Format the run-time url parameters (hhid, gid, etc)
            command["url_params"] = self._build_url_params(target)

            # Setup the required url route (/household/{}/players/{}/, etc)
            command["target_route"] = self._build_target_route(target)

            command["rest_name"] = self._build_rest_name(command_definition)

            command["return_type"] = self._get_return_types(command_definition)

            # Build the helper comments based on method input parameters
            command["arg_comments"] = self._build_arg_comments(target_args, required_args, optional_args, scope)

            if scope or self.api_version != "1":
                # If the command requires a token or using muse v2, figure out which client token to use
                command["oauth_token"] = "oauthToken"
                command["required_args"].append("oauthToken")
                command["required_args_map"].append({"name": "oauthToken", "isReserved": False})
                # importing oauth_server.Scopes class for the scope strings results in a circular import issue
                if re.sub("_", "", scope).lower() == "hhconfig":
                    command["set_hhConfigToken"] = True
                elif re.sub("_", "", scope).lower() == "hhconfigadmin":
                    command["set_hhConfigAdminToken"] = True
                else:
                    command["set_hhFakeToken"] = True

            if "oauthToken" in command["required_args"] or "oauthToken" in command["optional_args"]:
                # pass the token to the url request helper if the command requires one
                command["pass_oauthToken"] = True

            if self.api_version == "1" and self.is_rest_client:
                # allow the api key to be specified per command if muse v1 is used else
                # fall back to the stored automation one
                command["optional_args"].append("apiKey")
                command["optional_args_map"].append({"name": "apiKey", "isReserved": False})
                command["pass_apiKey"] = True

            commands.append(command)

        return commands

    def _build_rest_name(self, command_definition):
        rest_name = command_definition.attrib.get("restName", "")
        if rest_name != "":
            rest_name = "/" + rest_name

        # Hack to get around hand-made server endpoint for settings code. See SWPBL-119087
        if "/restrictedAdmin" in rest_name:
            rest_name = "/restricted-admin"
        elif "/protectedAdmin" in rest_name:
            rest_name = "/protected-admin"

        return rest_name

    def _build_url_params(self, target):
        params = ""
        if target != "none":
            if target == "householdId":
                params = ", self._museRestClient.hhid"
            elif target == "groupId":
                params += ", self._museRestClient.getGroupId()"
            elif target == "sessionId":
                params += ", sid"
            elif target == "playerId":
                params += ", self._museRestClient.uuid"
            elif target == "userId":
                params += ", self._museRestClient.userId"

        return params

    def _build_headers(self, target):
        headers = {}
        # HHID is automatically inserted in the template, no need to add it again
        if target:
            headers["header_key"] = target
            if target == "groupId":
                headers["header_value"] = "self._museRestClient.getGroupId()" \
                    if self.is_rest_client else "self._museConnection.getGroupId()"
            elif target == "sessionId":
                headers["header_value"] = "sid"
            elif target == "playerId":
                # The base rest and websocket clients hold the uuid differently
                headers["header_value"] = "self._museRestClient.uuid" \
                    if self.is_rest_client else "self._museConnection.uuid"
            elif target == "householdId":
                headers["header_value"] = "self._museRestClient.hhid" \
                    if self.is_rest_client else "self._museConnection.hhid"
            elif target == "userId":
                headers["header_value"] = "self._museRestClient.userId" \
                    if self.is_rest_client else "self._museConnection.userId"

        return headers

    def _build_target_route(self, target):
        route = ""
        if target != "none":
            if target == "householdId":
                route += "households/{}/"
            elif target == "groupId":
                route += "groups/{}/"
            elif target == "playerId":
                route += "players/{}/"
            elif target == "sessionId":
                route += "playbackSessions/{}/"
            elif target == "userId":
                route += "users/{}/"
        return route

    def _get_command_parameters(self, command, namespace):
        """
        Extract command parameters required and optional params for custom and non-custom/in-line defined dataTypes
        :param command:
        :param namespace:
        :return:
        """
        if command.find("arguments") is None:
            # arguments tag missing in the command
            return [], []
        elif 'type' in command.find("arguments").attrib.keys():
            # arguments tag present with "type" attribute -> Generally used for custom dataType declarations
            # These dataType declarations can be extracted from:
            # 1. within the namespace file
            # 2. file: xml/types/dataType.xml where dataType represents the name of the data type.

            # 1. Checking for custom dataType definitions within the namespace file
            dataType_attr = command.find("arguments").attrib["type"]
            ns_dataType_xml = [x for x in self.parser.xml if 'name' in x.attrib.keys()
                               and x.attrib['name'] == namespace][0].find('dataTypes')
            dataType_xml = None

            # custom dataTypes defined in namespace file
            if ns_dataType_xml is not None:
                # look for matching dataType
                dataType_xml = [x for x in ns_dataType_xml if 'name' in x.attrib.keys()
                                and x.attrib['name'] == dataType_attr]
                if len(dataType_xml) > 0:
                    # found a matching dataType
                    dataType_xml = dataType_xml[0]
                else:
                    # did not find a matching dataType
                    dataType_xml = None

            # 2. Checking for custom dataType definitions in parsed xml/types directory
            if dataType_xml is None:
                # check for custom dataType defined in parsed xml file: xml/types/dataType.xml
                dataType_xml = [x for x in self.parser.xml_types if 'name' in x.attrib.keys() and
                                x.attrib['name'] == dataType_attr][0]

            param_attr = dataType_xml.findall("parameter")

        else:
            # arguments tag present and argument parameters are defined in-line
            param_attr = command.find("arguments").findall("parameter")

        # Filter out parameter objects based on its sinceVersion and/or removedVersion
        param_attr = filter(lambda p: should_include(api_version=self.api_version,
                                                     component=p),
                            param_attr)

        req_param = [p for p in param_attr if p.attrib.get("required", "false") == "true"]
        opt_param = [p for p in param_attr if p.attrib.get("required", "false") == "false"]

        # Add key in attribute for isReserved to check if param name is a reserved keyword in Python
        for index, param in enumerate(req_param):
            param_name = param.attrib.get("name")
            if param_name is not None:
                if keyword.iskeyword(param_name):
                    req_param[index].set("isReserved", True)
                else:
                    req_param[index].set("isReserved", False)

        for index, param in enumerate(opt_param):
            param_name = param.attrib.get("name")
            if param_name is not None:
                if keyword.iskeyword(param_name):
                    opt_param[index].set("isReserved", True)
                else:
                    opt_param[index].set("isReserved", False)

        return req_param, opt_param

    def _build_arg_comments(self, target_args, required_args, optional_args, scope):
        arg_comments = []

        for arg in target_args:
            arg_comments.append({
                "arg_name": arg,
                "arg_type": "Required",
                "arg_description": " Target session ID",
            })

        for arg in required_args:
            desc = self._clean_description(arg.find("description"), "")
            arg_comments.append({
                "arg_name": arg.attrib["name"],
                "arg_type": "Required",
                "arg_description": " " + desc if desc else ""
            })

        for arg in optional_args:
            desc = self._clean_description(arg.find("description"), "")
            arg_comments.append({
                "arg_name": arg.attrib["name"],
                "arg_type": "Optional",
                "arg_description": " " + desc if desc else ""
            })

        if scope:
            arg_comments.append({
                "arg_name": "oauthToken",
                "arg_type": "Required",
                "arg_description": " {} scoped oauth token".format(scope),
            })
        else:
            if self.api_version != "1":
                arg_comments.append({
                    "arg_name": "oauthToken",
                    "arg_type": "Required",
                    "arg_description": " Muse v2 commands all require a token",
                })

        if self.api_version == "1" and self.is_rest_client:
            arg_comments.append({
                "arg_name": "apiKey",
                "arg_type": "Required",
                "arg_description": " X-Sonos-Api-Key value. If none is provided, the stored value is used",
            })

        return arg_comments

    def _get_return_types(self, command_definition):
        response = command_definition.find("response")
        if response is not None and response.attrib["responseType"] == "event":
            return_type = ""
            events = response.attrib["event"].split(" ")  # multiple events are space delimited
            for event in events:
                if event != "ok":
                    return_type += "{}Event ".format(event)
            return_type = return_type.rstrip()
        else:
            return_type = "No event"

        return return_type

    # endregion


# region Mustache View Class
class MuseRestClient(BaseMuseClientView):
    def __init__(self, api_version, parser):
        super(MuseRestClient, self).__init__(api_version=api_version, parser=parser, is_rest_client=True)

    # region Mustache Parameters
    def namespaces(self):
        return super(MuseRestClient, self).namespaces()

    def clients(self):
        clients = super(MuseRestClient, self).clients()

        for client in clients:
            print client["namespace_name"]
            for command in client["commands"]:
                print "\t" + command["command_name"]

        return clients
    # endregion


class MuseWebsocketClient(BaseMuseClientView):
    def __init__(self, api_version, parser):
        super(MuseWebsocketClient, self).__init__(api_version=api_version, parser=parser)

    # region Mustache Parameters
    def namespaces(self):
        return super(MuseWebsocketClient, self).namespaces()

    def clients(self):
        clients = super(MuseWebsocketClient, self).clients()

        # Print the client names to console
        for client in clients:
            print client["namespace_name"]
            for command in client["commands"]:
                print "\t" + command["command_name"]

        return clients


class MuseEventEnums(object):
    def __init__(self, parser):
        self.parser = parser

    def muse_events_enums(self):
        enums_collections = self._build_enums()

        # Print the enum names to console
        for enum_collection in enums_collections:
            print enum_collection

        return enums_collections

    def _build_enums(self):
        xml = []
        for namespace in self.parser.xml_enums:
            key = str(namespace.attrib['name']).capitalize()
            description = '{}'
            enum_collections = {
                "name": key,
                "description": description.format(" ".join(str(namespace[0].text).replace("\n", "").split())) if namespace[0].text is not None and  str(namespace[0].text).replace("\n", '').strip() else "Class description is missing",
                "xml_content": [x.attrib['name'] for x in namespace.findall('value')]
            }
            xml.append(enum_collections)
        return xml


class MuseEvents(object):
    def __init__(self, parser):
        self.parser = parser

    def muse_events(self):
        events = self._build_events()

        # Print the event names to console
        for event in events:
            print event["event_type"]

        return events

    def _build_events(self):
        event_definitions = self._get_event_definitions()

        muse_events = []
        for event_defintion in event_definitions:
            muse_events.append(self._build_event(event_defintion))

        # Go back and find events which are called out but not defined (quirk of the xml definition)
        missing_events = self._add_missing_events(self.parser.xml, event_definitions)
        muse_events.extend(missing_events)

        return muse_events

    def _get_event_definitions(self):
        event_definitions = []

        # Flatten events
        for namespace in self.parser.xml:
            if namespace.find("events") is not None:
                namespace_events = namespace.find("events").findall("event")
                event_definitions.extend(namespace_events)

        event_definitions = self._distinct(event_definitions, lambda xml: self._event_class_type(xml))
        event_definitions.sort(key=lambda xml: self._event_class_type(xml))

        return event_definitions

    def _event_class_type(self, event_definition):
        """
        Returns event class type if it exists, otherwise event name
        :param event_definition: xml definition of the event
        :return: event type if defined, otherwise event name
        """
        event_type = event_definition.attrib["type"] \
            if "type" in event_definition.attrib else event_definition.attrib["name"]
        return event_type[:1].upper() + event_type[1:]  # Capitalize

    def _distinct(self, li, comparator):
        """
        Takes a list and pulls distinct elements for a given comparison lambda
        :param li: list
        :param comparator: lambda to compare -> lambda l: l.model
        :return: unique list of elements
        """
        seen = []
        unique = []
        for l in li:
            if comparator(l) not in seen:
                seen.append(comparator(l))
                unique.append(l)
        return unique

    def _build_event(self, event_definition):
        event = {}

        event["event_type"] = self._event_class_type(event_definition)

        param_definitions = event_definition.findall("parameter")
        if param_definitions:
            event["event_body"] = {"parameters": []}
            for param_defintion in param_definitions:
                event["event_body"]["parameters"].append(param_defintion.attrib["name"])

        return event

    def _add_missing_events(self, api_definitions, event_definitions):
        """
        For events which are used, but not defined directly in the namespace xmls, add a simple stub class

        :param api_definitions:
        :param event_definitions:
        :return:
        """
        all_event_names = self._all_used_events(api_definitions)

        # Remove events which are both used and defined, leaving only stubbed events which are used but not called out
        for event_defintion in event_definitions:
            if self._event_class_type(event_defintion) in all_event_names:
                all_event_names.remove(self._event_class_type(event_defintion))

        events = []
        for event_name in all_event_names:
            events.append({
                "event_type": event_name
            })

        return events

    def _all_used_events(self, api_definitions):
        """
        Finds events which are used anywhere in the xmls, whether they are defined or not.

        :param api_definitions:
        :return: string list of all event names
        """
        all_event_names = []
        for api_definition in api_definitions:
            command_definitions = api_definition.find("commands").findall("command")

            for command_definition in command_definitions:
                response = command_definition.find("response")
                if response is not None and response.attrib["responseType"] == "event":
                    events = response.attrib["event"].split(" ")  # multiple events are space delimited
                    events = [ev for ev in events if "ok" != ev]
                    all_event_names.extend(events)

        # Filter out duplicates
        all_event_names = list(set(all_event_names))

        return [(e[:1].upper() + e[1:]) for e in all_event_names]  # Capitalize

    # endregion
# endregion

