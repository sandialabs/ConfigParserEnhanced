class LoadEnvCommon:
    """
    Provides a general base class for several modules in LoadEnv to share some
    common functions.
    """

    def get_formatted_err_msg(self, err_msg):
        """
        This helper method handles multiline error messages, rendering them
        like::

            |   ERROR:  Unable to find alias or environment name for system
            |           'machine-type-1' in keyword string 'bad_kw_str'.

        Parameters:
            err_msg (str):  The error message, potentially with multiple lines.

        Returns:
            str:  The formatted error message.
        """
        err_msg_lines = err_msg.split("\n")
        for idx, line in enumerate(err_msg_lines):
            if idx == 0:
                msg = f"|   ERROR:  {line}\n"
            else:
                msg += f"|           {line}\n"

        return msg

    def get_err_msg_for_list(self, err_msg, item_list):
        """
        Helper function to generate an error message using a list. Produces a
        message like the following::

            +=================================================================+
            |   ERROR:  {msg}
            |     - {item_list[0]}
            |     - {item_list[1]}
            |     - ...
            |     - {item_list[n]}
            +=================================================================+

        Parameters:
            err_msg (str):  The error message to print.  Can be multiline.
            item_list (list):  The list of items to print in the error message.

        Returns:
            str:  The formatted error message.
        """
        msg = ("\n+" + "="*78 + "+\n" +
               self.get_formatted_err_msg(err_msg))
        for item in item_list:
            msg += f"|     - {item}\n"
        msg += ("+" + "="*78 + "+\n")

        return msg
