##
## This code is part of the Jaudit utilty.
##
## (C) Copyright IBM 2023.
##
## This code is licensed under the Apache License, Version 2.0. You may
## obtain a copy of this license in the LICENSE.txt file in the root directory
## of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
##
## Any modifications or derivative works of this code must retain this
## copyright notice, and modified files need to carry a notice indicating
## that they have been altered from the originals.
##

class JarIdentifier:
    #
    # Called at startup for any initialization the class may need to do
    #
    # Returns: None
    #
    @classmethod
    def initialize(cls):
        return

    #
    # Called to verify that this analytic is supported.  This typically
    # means checking to see if the configuration contains the tables
    # needed for this analytic.  It can also be used to check for other
    # requirements.
    #
    # Returns: True or False
    #
    @classmethod
    def supported(cls):
        errorOut(cls.get_name() + " did not define supported() method. Disabling.")
        return False

    #
    # Define the priority of this analytic.  Priority is used only to
    # determine which analytic is the default if no analytic is
    # specified.  The analytic with the highest priority is the
    # default.  The current overall highest priority is 100
    # (class-fingerprint).
    #
    # Returns: Integer priority
    #
    @classmethod
    def priority(cls):
        return -1

    #
    # The name of the analytic
    #
    # Returns: String name
    #
    @classmethod
    def get_name(cls):
        raise NotImplementedError(str(cls)+": get_name() must be implemented")

    #
    # A brief description of the analytic
    #
    # Returns: String description
    #
    @classmethod
    def get_description(cls):
        return "No description provided"

    #
    # Does this analytic need to consume the raw data of an input stream?
    # An input stream is typically a Jar file.
    #
    # Returns: True or False
    #
    @classmethod
    def scans_input_stream(cls):
        return False

    #
    # Does this analytic need to consume the raw data of Java class file?
    #
    # Returns: True or False
    #
    @classmethod
    def scans_class_file(cls):
        return False
    
    #
    # Called if scans_input_stream() or scans_class_file is True; it
    # normally would save the input stream as the input source for the
    # analytic.  It would create a new stream that it forwards the
    # data read into.  This new input stream is returned to the
    # caller.
    #
    # This will create a "pipeline" of streams
    #
    # Returns: A new stream handle
    #
    def add_input_stream(self,streamIn):
        return streamIn


    #
    # Does the analytic need the Java class file to be decoded?
    #
    # Returns: True or False
    #
    @classmethod
    def uses_class_file(cls):
        return False

    #
    # If uses_class_file is True, then a JavaClass object will be
    # created from the class file and passed to add_class_file().
    # 
    # Returns: None
    #
    def add_class_file(self,cf):
        return

    #
    # Called after a jar file has been completely processed to allow
    # the analytic to do final version determination.
    #
    # Returns: none
    #
    def identify(self,inputHandle):
        raise NotImplementedError("identify() must be implemented")

