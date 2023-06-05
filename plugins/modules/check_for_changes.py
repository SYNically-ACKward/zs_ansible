#!/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: check for changes
short_description: This module will reach out to a Zscaler parent tenant and check to see if changes have been made in the specified timeframe.
version_added: "1.0.0"
description: This is my longer description explaining my test module.
options:
    parent:
        description: The Zscaler parent tenant.
        required: true
        type: str
author:
    - Ryan Ulrick (@SYNically-ACKward)
'''

EXAMPLES = r'''
- name: Check for changes
  synically-ackward.zs-ansible.check_for_changes:
    parent: "example_parent"
'''

RETURN = r'''
changed:
    description: Indicates whether changes were detected.
    type: bool
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from zia_talker.zia_talker import ZiaTalker
import datetime
import time
import io
import csv


def check_for_changes(module):
    parent = ZiaTalker(module.params['cloudId'])
    parent.authenticate(module.params['api_key'],
                        module.params['username'],
                        module.params['password'])
    current_timestamp = datetime.datetime.now().timestamp() * 1000
    # Perform the actions specific to your task using the Ansible module
    # Replace the placeholders with appropriate module invocations
    parent.add_auditlogEntryReport(startTime=(current_timestamp - (6 * 60 * 1000)),
                                   endTime=current_timestamp,
                                   actionTypes=["UPDATE", "CREATE"])
    while True:
        # Replace the placeholders with appropriate module invocations
        report_status = parent.list_auditlogEntryReport()
        if report_status['status'] == 'ERRORED':
            module.fail_json(msg="Error retrieving change report. Exiting Application.")
        elif report_status['status'] == 'COMPLETE':
            break

        time.sleep(5)

    # Replace the placeholders with appropriate module invocations
    file_content = parent.download_auditlogEntryReport()
    data_string = file_content.content.decode('utf-8')
    reader = csv.reader(io.StringIO(data_string))

    for i in range(5):
        next(reader)
    num_rows = sum(1 for row in reader) - 1

    if num_rows > 0:
        module.exit_json(changed=True)
    else:
        module.exit_json(changed=False)


def main():
    module_args = dict(
        cloudId=dict(type='str', required=True),
        username=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        api_key=dict(type='str', required=True, no_log=True),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    try:
        check_for_changes(module)
    except Exception as e:
        module.fail_json(msg="An error occurred: {}".format(str(e)))


if __name__ == '__main__':
    main()
