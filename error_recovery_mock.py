# DEVICES:[
#   {id: A; kind: SWITCH; qual: 0;};
#   {id: B; kind: SWITCH; qual: 1;};
# ];

class DeviceParsing():
    def __init__(self, mock_file):
        self.mock_file = mock_file
        self.index = -1  # not sure if this is necessary
        self.error_count = 0
        self.current_char = ""
        #self.expect_qualifier = ["SWITCH", "AND"]  # obvs there are more

    def error(self, msg, expect_next_list):
        end_of_file = False
        recovered = False
        print(f"ERROR at index {self.index}: " + msg +
              f", received {self.current_char}")
        self.error_count += 1

        # while True:
        #     for expectedsymbol in expect_next_list:
        #         while self.current_char != ";":
        #             self.next_char()
        #
        #         try:
        #             self.next_char()
        #         except IndexError:
        #             print("reached end of file!")
        #             end_of_file = True
        #             break
        #
        #         if self.current_char == expectedsymbol:
        #             recovered=True
        #             break
        #
        #     if end_of_file:
        #         break
        #     if recovered:
        #         break


        while True:
            while self.current_char != ";":
                self.next_char()
            #found a semi colon, now need to check if the expected element
            # is next
            try:
                self.next_char()
            except IndexError:
                print("reached end of file!")
                end_of_file = True
                break

            if self.current_char in expect_next_list:
                # found the character we want to keep parsing, therefore we
                # resume in the parsing
                break

            #below does the same i think
            # found_character = False
            # for i in range(len(expect_next_list)):  # expected symbols have
            # # to be in order of expectation!
            #     if self.current_char == expect_next_list[i]:
            #         found_character = True
            #         break
            #         #will this break the for loop? or
            #         # the while loop?
            # if found_character:
            #     break


            # this currently will not deal nicely an error at the end of the
            # file / if we miss a semi-colon at the end??!!! infinite loop
            # TODO: what if error recovery means that skip the whole file...



        # will break out if we've found the right character, or if we've
        # reached end of file.........

        #TODO: what if we reach the end of the file??? :/ eek
        # equivalent to if we are unable to resume parsing

        # will it just work out?

    def next_char(self):
        self.index += 1
        self.current_char = self.mock_file[self.index]

    def parse_device_list(self):
        while True:
            self.next_char()
            if self.current_char != "DEVICES":
                self.error(f"no devices keyword", "DEVICES")
                # will have skipped to the final semi colon
                # more likely that it will just skip to the end of the file!
                # self.parse_connections()
                break
            # self.next_char()
            # if self.current_char != ":":
            #     self.error("expected :")
            #     break
            self.next_char()
            if self.current_char != "[":
                self.error("expected [", ["CONNECTIONS", "MONITORS"])  # but
                # it could also be end of file????? here/only devices
                break

            # if we get here we got DEVICES [
            self.next_char()  # set up so current char is {

            parsing_devices = True
            while parsing_devices:
                missing_semi_colon = self.parse_device(self.error_count)
                #TODO: what to do if there is a missing semi_colon????
                #nothing????? what is the consequence....

                if missing_semi_colon:
                    pass
                    #if missed one, we would skip until we get { or ]
                    #dont actually need to do anything?

                #self.next_char() #issue is here....
                if self.current_char == "{":
                    # more devices to parse
                    parsing_devices = True
                    #return keep_parsing
                elif self.current_char == "]":
                    # reached end of device list
                    # if self.error_count == 0:
                    #     print("successfully parsed the device")
                    #     print(f"device {dev_id}-{dev_kind}-{dev_qual}")
                        # can move on back to rest of devices
                    parsing_devices = False
                    #return keep_parsing
                else:
                    #TODO: what if it is neither of those???
                    # is this when there is an error at the end of device
                    # lists?
                    print("sort this problem out")



            if self.current_char != "]":
                self.error("expected ]", ["CONNECTIONS", "MONITORS"])
                break

            self.next_char()
            if self.current_char != ";":
                self.error("expected ;", ["MONITORS"])
                #TODO: not sure if it's connections/monitors
                break

            # I mean it has to be 0 surely?
            if self.error_count == 0:
                print("successfully parsed a device list!")
                return True
            else:
                print(f"found {self.error_count} error(s)")
                break

        # only get here if there is an error with the 'outer' device list
        # wrapper
        print("did not manage to parse the device list perfectly")
        # wish this could be more informative.......
        # maybe thats for self.error / scanner
        #what is the point of this code below huhh/???
        if self.error_count != 0:
            return False
        else:
            return True

    def parse_device(self, previous_errors):
        missing_device_semi_colon = False
        while True:
            # self.next_char()
            if self.current_char != "{":
                self.error("expected {",["{","]"])
                # go ot the next device we can parse
                # TODO: what if there is only one device?
                # TODO: uGH MY BRAIN CAN'T COPE something else is wrong here
                #  i can sense it
                # the list should be searched linearly.... in case someone
                # just puts ;] in there as a mistake.. deal with later rah
                break

            #now we can parse the id section
            self.next_char()  # current char should be "id"
            missing_semi_colon, dev_id = self.parse_device_id()

            if missing_semi_colon:
                break
                #helps with the looping if it is break instead of continue

            missing_semi_colon, dev_kind = self.parse_device_kind()

            if missing_semi_colon:
                break

            if self.current_char == "qual":  # if it is there, we will parse it
                missing_semi_colon, dev_qual = self.parse_device_qual()
                if missing_semi_colon:
                    break
            else:
                dev_qual = None

            if self.current_char != "}":
                self.error("expected }",["{","]"])
                break

            self.next_char()
            if self.current_char != ";":
                self.error("expected ;",["{","]"])
                missing_device_semi_colon = True
                break

            #if we get here we have done a whole device!
            if self.error_count - previous_errors == 0:
                print(f"successfully parsed the device: {dev_id}-{dev_kind}-{dev_qual}")
                # TODO: what if there are residue errors from other devices?
                # need a way of counting the additional errors which have
                # occured in this call of the parse_device...
                self.next_char() #setting up in case of errors....
                break
            else:
                print(f"did not successfully parse the device sad.. would have "
                      f"attempted to build device "
                      f"{dev_id}-{dev_kind}-{dev_qual}")
                self.next_char()
                break
        return missing_device_semi_colon


    def parse_device_id(self):
        missing_semi_colon = False
        dev_name_string = None
        while True:
            if self.current_char != "id":
                self.error("expected id keyword here", ["kind"])
                break

            self.next_char()
            if self.current_char != ":":
                self.error("expected : here", ["kind"])
                break

            self.next_char()
            if not self.current_char.isalnum():
                self.error("OI this is not alnum --> SYNTAX error",["kind"])

                break
            dev_name_string = self.current_char

            self.next_char()
            if self.current_char != ";":
                self.error("missing semicolon", ["{"])
                missing_semi_colon = True
                break
                # should i just call parse_device here????

            self.next_char()  #setting up for next function

            #current_char should be "kind" here
            break

        return missing_semi_colon, dev_name_string

    def parse_device_kind(self):
        missing_semi_colon = False
        dev_kind = None
        while True:
            if self.current_char != "kind":
                self.error("expected kind keyword here", ["qual", "}"])
                break

            self.next_char()
            if self.current_char != ":":
                self.error("expected : here", ["qual", "}"])
                break

            self.next_char()
            if not self.current_char.isalnum():
                # actually this is
                # different in final code (checking if its a valid name only)
                self.error("OI this is not alnum --> SYNTAX error",["qual", "}"])
                break
            dev_kind = self.current_char

            self.next_char()
            if self.current_char != ";":
                self.error("missing semicolon", ["{"])
                missing_semi_colon = True
                break

            self.next_char()  #either qual or }
            break

        return missing_semi_colon, dev_kind

    def parse_device_qual(self):
        missing_semi_colon = False
        dev_qual = None
        while True:
            if self.current_char != "qual":
                self.error("expected qual keyword here", ["}"])
                break

            self.next_char()
            if self.current_char != ":":
                self.error("expected : here", ["}"])
                break

            self.next_char()
            if not self.current_char.isnumeric():
                # actually this is
                # different in final code (checking if its a valid name only)
                self.error("OI this is not numeric --> SYNTAX error",
                           [ "}"])
                break
            dev_qual = self.current_char

            self.next_char()
            if self.current_char != ";":
                self.error("missing semicolon", ["{"])
                missing_semi_colon = True
                break

            self.next_char()  # should be }
            break

        return missing_semi_colon, dev_qual



correct_file = [
  "DEVICES",  "[", "{", "id", ":", "A", ";", "kind", ":", "SWITCH", ";" , "qual", ":", "0", ";", "}", ";",
  "{", "id", ":", "B", ";", "kind", ":", "SWITCH", ";", "qual", ":", "1", ";", "}", ";", "]", ";",
]

# dp = DeviceParsing(correct_file)
#
# dp.parse_device_list()

incorrect_file = [
  "DEVICES",  "[",
    "{",
    "id", "elephant", "**will skip this error*", ";",
    "kind", ":", "SWITCH", ";" ,
    "bepbop", ":", "0", ";",  #this error causes the device stuff not to be
    # built not that it matters....
    "}", ";",
  "{",
    "id", "mistake", "B", ";",
    "kind", ":", "noerrorherebcnotsyntax", ";",
    #"qual", ":", "1", ";",
    "}", ";",
    "{",
    "id", ":", "C", ";",
    "kind", ":", "noerrorherebcnotsyntax", ";",
    "qual", ":", "1", ";",
    "}", ";",
    "{",
    "id", ":", "D", ";",
    "meh", ":", "noerrorherebcnotsyntax", ";",
    "qual", ":", "1", ";",
    "}", ";",
    "]",
    ";",
]

dp = DeviceParsing(incorrect_file)
dp.parse_device_list()
#
# order_incorrect_file = [
#   "DEVICES",  "[",
#     "{",
#     "id", "elephant", "**will skip this error*", ";",
#     "kind", ":", "SWITCH", ";" ,
#     "qual", ";", "]", ";",
#     "]", ";", #gonna get confused here!
#   "{",
#     "id", ":", "B", ";",
#     "kind", ":", "will never even parse", ";",
#     #"qual", ":", "1", ";",
#     "}", ";",
#     "]",
#     ";",
# ]
#
# dp = DeviceParsing(order_incorrect_file)
# dp.parse_device_list()



# end_incorrect_file = [
#   "DEVICES",  "er",
#     "{",
#     "id", "elephant", "**will skip this error*", ";",
#     "kind", ":", "SWITCH", ";" ,
#     "qual", ":", "0", ";",
#     "]", ";",
#   "{",
#     "id", ":", "B", ";",
#     "kind", ":", "88(()**errorhere", ";",
#     #"qual", ":", "1", ";",
#     "}", ";",
#     "]",
#     ";",
#     "CONNECTIONS"
# ]
# if devices is wrong all together you need to do with end of file stuff
# or not bc its a scanner1!!!!!
# dp = DeviceParsing(end_incorrect_file)
# dp.parse_device_list()