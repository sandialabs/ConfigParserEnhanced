import re

class FormattedMsg:
    def get_formatted_msg(self, msg, kind="ERROR", extras=""):
        """
        This helper method handles multiline messages, rendering them like::

            +=================================================================+
            |   {kind}:  Unable to find alias or environment name for system
            |            'machine-type-1' in keyword string 'bad_kw_str'.
            |   {extras}
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
        msg = re.sub(r"\s+\n", "\n", msg)  # Remove trailing whitespace

        return msg

    def get_msg_for_list(self, msg, item_list, kind="ERROR", extras=""):
        """
        Helper function to generate a message using a list. Produces a message
        like the following::

            +=================================================================+
            |   {kind}:  {msg}
            |     - {item_list[0]}
            |     - {item_list[2]}
            |     - ...
            |     - {item_list[n]}
            |   {extras}
            +=================================================================+

        Parameters:
            msg (str):  The error message to print.  Can be multiline.
            item_list (list):  The list of items to print in the error message.
            kind (str):  The kind of message being generated, e.g., "ERROR",
                "WARNING", "INFO", etc.

        Returns:
            str:  The formatted message.
        """
        new_extras = ""
        for item in item_list:
            new_extras += f"  - {item}\n"
        new_extras += extras
        msg = self.get_formatted_msg(msg, kind=kind, extras=new_extras)
        return msg
