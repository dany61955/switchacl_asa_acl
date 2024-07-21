# library/process_outputs.py
# - name: Process outputs using custom module
#   process_outputs:
#     pre_reload_asa_context_output: "{{ pre_reload_asa_context_output }}"
#     item_context: "{{ item_context }}"
#     input_cmds: "{{ input_cmds }}"
#   register: result

# - name: Debug the processed_output variable
#   debug:
#     msg: "Processed Output: {{ result.processed_output }}"

from ansible.module_utils.basic import AnsibleModule

def process_outputs(pre_reload_asa_context_output, item_context, input_cmds):
    result = []
    for context in pre_reload_asa_context_output:
        if context.get('name') == item_context:
            for cmd_output in context.get('cmd_outputs', []):
                if cmd_output.get('item') in input_cmds:
                    stdout_value = cmd_output.get('stdout', '')
                    if stdout_value != '':
                        result.append(stdout_value)
                    else:
                        result.append('Empty')
    return result

def run_module():
    module_args = dict(
        pre_reload_asa_context_output=dict(type='list', required=True),
        item_context=dict(type='str', required=True),
        input_cmds=dict(type='list', required=True)
    )

    result = dict(
        changed=False,
        processed_output=[]
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    pre_reload_asa_context_output = module.params['pre_reload_asa_context_output']
    item_context = module.params['item_context']
    input_cmds = module.params['input_cmds']

    result['processed_output'] = process_outputs(pre_reload_asa_context_output, item_context, input_cmds)

    module.exit_json(**result)

if __name__ == '__main__':
    run_module()
