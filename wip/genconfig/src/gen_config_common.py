class GenConfigCommon:
    """
    Provides a general base class for several modules in GenConfig to share
    some common functions.
    """

    def get_formatted_msg(self, msg, kind="ERROR", extras=""):
        """
        This helper method handles multiline messages, rendering them like::

            +=================================================================+
            |   {kind}:  Unable to find alias or environment name for system
            |            'machine-type-5' in keyword string 'bad_kw_str'.
            +=================================================================+

        Parameters:
            msg (str):  The error message, potentially with multiple lines.
            kind (str):  The kind of message being generated, e.g., "ERROR",
                "WARNING", "INFO", etc.
            extras (str):  Any extra text to include after the initial ``msg``.

        Returns:
            str:  The formatted message.
        """
        for idx, line in enumerate(msg.splitlines()):
            if idx == 0:
                msg = f"|   {kind}:  {line}\n"
            else:
                msg += f"|           {line}\n"
        for extra in extras.splitlines():
            msg += f"|   {extra}\n"
        msg = "\n+" + "="*78 + "+\n" + msg + "+" + "="*78 + "+\n"
        return msg

    def get_msg_for_list(self, msg, item_list, kind="ERROR"):
        """
        Helper function to generate a message using a list. Produces a message
        like the following::

            +=================================================================+
            |   {kind}:  {msg}
            |     - {item_list[0]}
            |     - {item_list[1]}
            |     - ...
            |     - {item_list[n]}
            +=================================================================+

        Parameters:
            msg (str):  The error message to print.  Can be multiline.
            item_list (list):  The list of items to print in the error message.
            kind (str):  The kind of message being generated, e.g., "ERROR",
                "WARNING", "INFO", etc.

        Returns:
            str:  The formatted message.
        """
        extras = ""
        for item in item_list:
            extras += f"  - {item}\n"
        msg = self.get_formatted_msg(msg, kind=kind, extras=extras)
        return msg
