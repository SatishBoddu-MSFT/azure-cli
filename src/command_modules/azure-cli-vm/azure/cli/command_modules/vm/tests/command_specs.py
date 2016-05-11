﻿# AZURE CLI VM TEST DEFINITIONS
import json

from azure.cli.utils.command_test_script import CommandTestScript, JMESPathComparator

#pylint: disable=method-hidden
class VMImageListByAliasesScenarioTest(CommandTestScript):

    def test_body(self):
        result = self.run('vm image list --offer ubuntu -o tsv')
        assert result.index('14.04.4-LTS') >= 0

    def __init__(self):
        super(VMImageListByAliasesScenarioTest, self).__init__(None, self.test_body, None)

class VMImageListThruServiceScenarioTest(CommandTestScript):

    def test_body(self):
        cmd = ('vm image list -l westus --publisher Canonical --offer '
               'Ubuntu_Snappy_Core -o tsv --all')
        result = self.run(cmd)
        assert result.index('15.04') >= 0

    def __init__(self):
        super(VMImageListThruServiceScenarioTest, self).__init__(None, self.test_body, None)

class VMListFoldedScenarioTest(CommandTestScript):

    def __init__(self):
        super(VMListFoldedScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        all_vms = json.loads(self.run('vm list -o json'))
        some_vms = json.loads(self.run('vm list -g travistestresourcegroup -o json'))
        assert len(all_vms) > len(some_vms)

class VMListIPAddressesScenarioTest(CommandTestScript):

    def __init__(self):
        self.deployment_name = 'azurecli-test-deployment-vm-list-ips'
        self.resource_group = 'cliTestRg_VmListIpAddresses'
        self.location = 'westus'
        self.vm_name = 'vm-with-public-ip'
        self.ip_allocation_method = 'Dynamic'
        super(VMListIPAddressesScenarioTest, self).__init__(
            self.set_up,
            self.test_body,
            self.tear_down)

    def set_up(self):
        self.run('resource group create --location {} --name {}'.format(
            self.location,
            self.resource_group))

    def test_body(self):
        # Expecting no results at the beginning
        self.test('vm list-ip-addresses --resource-group {}'.format(self.resource_group), None)
        self.run(['vm', 'create', '--resource-group', self.resource_group,
                  '--location', self.location,
                  '-n', self.vm_name, '--admin-username', 'ubuntu',
                  '--image', 'Canonical:UbuntuServer:14.04.4-LTS:latest',
                  '--admin-password', 'testPassword0', '--deployment-name', self.deployment_name,
                  '--public-ip-address-allocation', self.ip_allocation_method,
                  '--public-ip-address-type', 'new'])
        # Expecting the one we just added
        self.test('vm list-ip-addresses --resource-group {}'.format(self.resource_group),
                  [
                      JMESPathComparator('length(@)', 1),
                      JMESPathComparator('[0].virtualMachine.name', self.vm_name),
                      JMESPathComparator('[0].virtualMachine.resourceGroup', self.resource_group),
                      JMESPathComparator(
                          'length([0].virtualMachine.network.publicIpAddresses)',
                          1),
                      JMESPathComparator(
                          '[0].virtualMachine.network.publicIpAddresses[0].ipAllocationMethod',
                          self.ip_allocation_method),
                      JMESPathComparator(
                          'type([0].virtualMachine.network.publicIpAddresses[0].ipAddress)',
                          'string')]
                 )

    def tear_down(self):
        self.run('resource group delete --name {}'.format(self.resource_group))

class VMSizeListScenarioTest(CommandTestScript):

    def __init__(self):
        super(VMSizeListScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm size list --location westus', JMESPathComparator('type(@)', 'array'))

class VMShowScenarioTest(CommandTestScript):

    def __init__(self):
        self.deployment_name = 'azurecli-test-deployment-vm-show'
        self.resource_group = 'cliTestRg_VmShow'
        self.location = 'westus'
        self.vm_name = 'vm-show'
        super(VMShowScenarioTest, self).__init__(
            self.set_up,
            self.test_body,
            self.tear_down)

    def set_up(self):
        self.run('resource group create --location {} --name {}'.format(
            self.location,
            self.resource_group))

    def test_body(self):
        self.run(['vm', 'create', '--resource-group', self.resource_group,
                  '--location', self.location,
                  '-n', self.vm_name, '--admin-username', 'ubuntu',
                  '--image', 'Canonical:UbuntuServer:14.04.4-LTS:latest',
                  '--admin-password', 'testPassword0', '--deployment-name', self.deployment_name])
        self.test('vm show --resource-group {} --name {} --expand instanceView'.format(
            self.resource_group, self.vm_name),
                  [
                      JMESPathComparator('type(@)', 'object'),
                      JMESPathComparator('name', self.vm_name),
                      JMESPathComparator('location', self.location),
                      JMESPathComparator('resourceGroup', self.resource_group),
                  ])

    def tear_down(self):
        self.run('resource group delete --name {}'.format(self.resource_group))

class VMImageListOffersScenarioTest(CommandTestScript):

    def __init__(self):
        self.location = 'westus'
        self.publisher_name = 'Canonical'
        super(VMImageListOffersScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm image list-offers --location {} --publisher-name {}'.format(
            self.location, self.publisher_name),
                  [
                      JMESPathComparator('type(@)', 'array'),
                      # all results should have location has set in the test
                      JMESPathComparator("length([?location == '{}']) == length(@)".format(
                          self.location),
                                         True),
                      # all results should have the correct publisher name
                      JMESPathComparator(
                          "length([].id.contains(@, '/Publishers/{}'))".format(self.publisher_name),
                          6),
                  ])

class VMImageListPublishersScenarioTest(CommandTestScript):

    def __init__(self):
        self.location = 'westus'
        super(VMImageListPublishersScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm image list-publishers --location {}'.format(self.location),
                  [
                      JMESPathComparator('type(@)', 'array'),
                      # all results should have location has set in the test
                      JMESPathComparator("length([?location == '{}']) == length(@)".format(
                          self.location),
                                         True),
                  ])

class VMImageListSkusScenarioTest(CommandTestScript):

    def __init__(self):
        self.location = 'westus'
        self.publisher_name = 'Canonical'
        self.offer = 'UbuntuServer'
        super(VMImageListSkusScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm image list-skus --location {} --publisher-name {} --offer {}'.format(
            self.location, self.publisher_name, self.offer),
                  [
                      JMESPathComparator('type(@)', 'array'),
                      # all results should have location has set in the test
                      JMESPathComparator("length([?location == '{}']) == length(@)".format(
                          self.location),
                                         True),
                      # all results should have the correct publisher name
                      JMESPathComparator(
                          "length([].id.contains(@, '/Publishers/{}/ArtifactTypes/VMImage/Offers/{}/Skus/'))".format( #pylint: disable=line-too-long
                              self.publisher_name, self.offer),
                          27),
                  ])

class VMImageShowScenarioTest(CommandTestScript):

    def __init__(self):
        self.location = 'westus'
        self.publisher_name = 'Canonical'
        self.offer = 'UbuntuServer'
        self.skus = '14.04.2-LTS'
        self.version = '14.04.201503090'
        super(VMImageShowScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm image show --location {} --publisher-name {} --offer {} --skus {} --version {}'.format( #pylint: disable=line-too-long
            self.location, self.publisher_name, self.offer, self.skus, self.version),
                  [
                      JMESPathComparator('type(@)', 'object'),
                      JMESPathComparator('location', self.location),
                      JMESPathComparator('name', self.version),
                      # all results should have the correct publisher name
                      JMESPathComparator(
                          "contains(id, '/Publishers/{}/ArtifactTypes/VMImage/Offers/{}/Skus/{}/Versions/{}')".format( #pylint: disable=line-too-long
                              self.publisher_name, self.offer, self.skus, self.version),
                          True),
                  ])

class VMListSizesScenarioTest(CommandTestScript):

    def __init__(self):
        self.deployment_name = 'azurecli-test-deployment-vm-list-sizes'
        self.resource_group = 'cliTestRg_VmListSizes'
        self.location = 'westus'
        self.vm_name = 'vm-show'
        super(VMListSizesScenarioTest, self).__init__(self.set_up, self.test_body, self.tear_down)

    def set_up(self):
        self.run('resource group create --location {} --name {}'.format(
            self.location,
            self.resource_group))

    def test_body(self):
        self.run(['vm', 'create', '--resource-group', self.resource_group,
                  '--location', self.location,
                  '-n', self.vm_name, '--admin-username', 'ubuntu',
                  '--image', 'Canonical:UbuntuServer:14.04.4-LTS:latest',
                  '--admin-password', 'testPassword0', '--deployment-name', self.deployment_name])
        self.test(
            'vm list-sizes --resource-group {} --name {}'.format(
                self.resource_group,
                self.vm_name),
            JMESPathComparator('type(@)', 'array'))

    def tear_down(self):
        self.run('resource group delete --name {}'.format(self.resource_group))

class VMGeneralizeScenarioTest(CommandTestScript):

    def __init__(self):
        self.deployment_name = 'azurecli-test-deployment-vm-generalize'
        self.resource_group = 'cliTestRg_VmGeneralize'
        self.location = 'westus'
        self.vm_name = 'vm-generalize'
        super(VMGeneralizeScenarioTest, self).__init__(self.set_up, self.test_body, self.tear_down)

    def set_up(self):
        self.run('resource group create --location {} --name {}'.format(
            self.location,
            self.resource_group))

    def test_body(self):
        self.run(['vm', 'create', '--resource-group', self.resource_group,
                  '--location', self.location,
                  '--name', self.vm_name, '--admin-username', 'ubuntu',
                  '--image', 'Canonical:UbuntuServer:14.04.4-LTS:latest',
                  '--admin-password', 'testPassword0', '--deployment-name', self.deployment_name])
        self.run('vm power-off --resource-group {} --name {}'.format(
            self.resource_group, self.vm_name))
        # Should be able to generalize the VM after it has been stopped
        self.test(
            'vm generalize --resource-group {} --name {}'.format(
                self.resource_group,
                self.vm_name), None)

    def tear_down(self):
        self.run('resource group delete --name {}'.format(self.resource_group))

class VMCreateAndStateModificationsScenarioTest(CommandTestScript):

    def __init__(self):
        self.deployment_name = 'azurecli-test-deployment-vm-state-mod'
        self.resource_group = 'cliTestRg_VmStateMod'
        self.location = 'westus'
        self.vm_name = 'vm-state-mod'
        super(VMCreateAndStateModificationsScenarioTest, self).__init__(
            self.set_up,
            self.test_body,
            self.tear_down)

    def set_up(self):
        self.run('resource group create --location {} --name {}'.format(
            self.location,
            self.resource_group))

    def _check_vm_power_state(self, expected_power_state):
        self.test(
            'vm show --resource-group {} --name {} --expand instanceView'.format(
                self.resource_group,
                self.vm_name),
            [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('name', self.vm_name),
                JMESPathComparator('resourceGroup', self.resource_group),
                JMESPathComparator('length(instanceView.statuses)', 2),
                JMESPathComparator(
                    'instanceView.statuses[0].code',
                    'ProvisioningState/succeeded'),
                JMESPathComparator('instanceView.statuses[1].code', expected_power_state),
            ])

    def test_body(self):
        # Expecting no results
        self.test('vm list --resource-group {}'.format(self.resource_group), None)
        self.run(['vm', 'create', '--resource-group', self.resource_group,
                  '--location', self.location,
                  '--name', self.vm_name, '--admin-username', 'ubuntu',
                  '--image', 'Canonical:UbuntuServer:14.04.4-LTS:latest',
                  '--admin-password', 'testPassword0', '--deployment-name', self.deployment_name])
        # Expecting one result, the one we created
        self.test('vm list --resource-group {}'.format(self.resource_group), [
            JMESPathComparator('length(@)', 1),
            JMESPathComparator('[0].resourceGroup', self.resource_group),
            JMESPathComparator('[0].name', self.vm_name),
            JMESPathComparator('[0].location', self.location),
            JMESPathComparator('[0].provisioningState', 'Succeeded'),
        ])
        self._check_vm_power_state('PowerState/running')
        self.run('vm power-off --resource-group {} --name {}'.format(
            self.resource_group, self.vm_name))
        self._check_vm_power_state('PowerState/stopped')
        self.run('vm start --resource-group {} --name {}'.format(
            self.resource_group, self.vm_name))
        self._check_vm_power_state('PowerState/running')
        self.run('vm restart --resource-group {} --name {}'.format(
            self.resource_group, self.vm_name))
        self._check_vm_power_state('PowerState/running')
        self.run('vm deallocate --resource-group {} --name {}'.format(
            self.resource_group, self.vm_name))
        self._check_vm_power_state('PowerState/deallocated')
        self.run('vm delete --resource-group {} --name {}'.format(
            self.resource_group, self.vm_name))
        # Expecting no results
        self.test('vm list --resource-group {}'.format(self.resource_group), None)

    def tear_down(self):
        self.run('resource group delete --name {}'.format(self.resource_group))

class VMAvailSetScenarioTest(CommandTestScript):

    def __init__(self):
        self.resource_group = 'cliTestRg_Availset'
        self.location = 'westus'
        self.name = 'availset-test'
        super(VMAvailSetScenarioTest, self).__init__(self.set_up, self.test_body, self.tear_down)

    def set_up(self):
        # TODO Create the resource group and availability set here once the command exists
        pass

    def test_body(self):
        self.test('vm availset list --resource-group {}'.format(self.resource_group), [
            JMESPathComparator('length(@)', 1),
            JMESPathComparator('[0].name', self.name),
            JMESPathComparator('[0].resourceGroup', self.resource_group),
            JMESPathComparator('[0].location', self.location),
        ])
        self.test('vm availset list-sizes --resource-group {} --name {}'.format(
            self.resource_group, self.name), JMESPathComparator('type(@)', 'array'))
        self.test('vm availset show --resource-group {} --name {}'.format(
            self.resource_group, self.name), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('name', self.name),
                JMESPathComparator('resourceGroup', self.resource_group),
                JMESPathComparator('location', self.location)])
        self.test('vm availset delete --resource-group {} --name {}'.format(
            self.resource_group, self.name), None)
        self.test('vm availset list --resource-group {}'.format(
            self.resource_group), None)

    def tear_down(self):
        pass

class VMExtensionsScenarioTest(CommandTestScript):

    def __init__(self):
        self.resource_group = 'cliTestRg_VMExtensions'
        self.location = 'westus'
        self.vm_name = 'windows-ext'
        self.extension_name = 'Microsoft.Insights.VMDiagnosticsSettings'
        super(VMExtensionsScenarioTest, self).__init__(self.set_up, self.test_body, self.tear_down)

    def set_up(self):
        # TODO Create the resource group and VM with extension here once the command exists
        pass

    def test_body(self):
        self.test('vm extension show --resource-group {} --vm-name {} --name {}'.format(
            self.resource_group, self.vm_name, self.extension_name), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('name', self.extension_name),
                JMESPathComparator('resourceGroup', self.resource_group)])
        self.test('vm extension delete --resource-group {} --vm-name {} --name {}'.format(
            self.resource_group, self.vm_name, self.extension_name),
                  None)

    def tear_down(self):
        pass

class VMMachineExtensionImageScenarioTest(CommandTestScript):

    def __init__(self):
        self.location = 'westus'
        self.publisher = 'Microsoft.Azure.Diagnostics'
        self.type = 'IaaSDiagnostics'
        self.version = '1.6.4.0'
        super(VMMachineExtensionImageScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm machine-extension-image list-types --location {} --publisher-name {}'.format(
            self.location, self.publisher), [
                JMESPathComparator('type(@)', 'array'),
                JMESPathComparator("length([?location == '{}']) == length(@)".format(self.location),
                                   True),
            ])
        self.test('vm machine-extension-image list-versions --location {} --publisher-name {} --type {}'.format( #pylint: disable=line-too-long
            self.location, self.publisher, self.type), [
                JMESPathComparator('type(@)', 'array'),
                JMESPathComparator("length([?location == '{}']) == length(@)".format(self.location),
                                   True),
            ])
        self.test('vm machine-extension-image show --location {} --publisher-name {} --type {} --version {}'.format( #pylint: disable=line-too-long
            self.location, self.publisher, self.type, self.version), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('location', self.location),
                JMESPathComparator("contains(id, '/Providers/Microsoft.Compute/Locations/{}/Publishers/{}/ArtifactTypes/VMExtension/Types/{}/Versions/{}')".format( #pylint: disable=line-too-long
                    self.location, self.publisher, self.type, self.version
                ), True)])

class VMScaleSetGetsScenarioTest(CommandTestScript):

    def __init__(self):
        self.resource_group = 'cliTestRg_ScaleSet1'
        self.ss_name = 'scaleset1'
        self.location = 'westus'
        super(VMScaleSetGetsScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm scaleset list-all', [
            JMESPathComparator('type(@)', 'array')])
        self.test('vm scaleset list --resource-group {}'.format(
            self.resource_group), [
                JMESPathComparator('type(@)', 'array'),
                JMESPathComparator('length(@)', 1),
                JMESPathComparator('[0].name', self.ss_name),
                JMESPathComparator('[0].location', self.location),
                JMESPathComparator('[0].resourceGroup', self.resource_group)])
        self.test('vm scaleset list-skus --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name),
                  JMESPathComparator('type(@)', 'array'))
        self.test('vm scaleset show --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('name', self.ss_name),
                JMESPathComparator('location', self.location),
                JMESPathComparator('resourceGroup', self.resource_group)])
        self.test('vm scaleset get-instance-view --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('type(virtualMachine)', 'object'),
                JMESPathComparator('type(statuses)', 'array')])

class VMScaleSetStatesScenarioTest(CommandTestScript):

    def __init__(self):
        self.resource_group = 'cliTestRg_ScaleSet1'
        self.ss_name = 'scaleset1'
        super(VMScaleSetStatesScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm scaleset power-off --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), None)
        self.test('vm scaleset start --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), None)
        self.test('vm scaleset restart --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), None)
        self.test('vm scaleset update-instances --resource-group {} --name {} --instance-ids 0'.format( #pylint: disable=line-too-long
            self.resource_group, self.ss_name), None)

class VMScaleSetDeleteScenarioTest(CommandTestScript):

    def __init__(self):
        self.resource_group = 'cliTestRg_ScaleSet1'
        self.ss_name = 'scaleset1'
        self.vm_count = 5
        self.instance_id_to_delete = 1
        super(VMScaleSetDeleteScenarioTest, self).__init__(None, self.test_body, None)

    def test_body(self):
        self.test('vm scaleset list --resource-group {}'.format(
            self.resource_group), [
                JMESPathComparator('type(@)', 'array'),
                JMESPathComparator('length(@)', 1),
                JMESPathComparator('[0].name', self.ss_name),
                JMESPathComparator('[0].resourceGroup', self.resource_group)])
        self.test('vm scaleset get-instance-view --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('type(virtualMachine)', 'object'),
                JMESPathComparator('virtualMachine.statusesSummary[0].count', self.vm_count)])
        self.test('vm scaleset delete-instances --resource-group {} --name {} --instance-ids {}'.format( #pylint: disable=line-too-long
            self.resource_group, self.ss_name, self.instance_id_to_delete), None)
        self.test('vm scaleset get-instance-view --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), [
                JMESPathComparator('type(@)', 'object'),
                JMESPathComparator('type(virtualMachine)', 'object'),
                JMESPathComparator('virtualMachine.statusesSummary[0].count', self.vm_count-1)])
        self.test('vm scaleset deallocate --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), None)
        self.test('vm scaleset delete --resource-group {} --name {}'.format(
            self.resource_group, self.ss_name), None)
        self.test('vm scaleset list --resource-group {}'.format(
            self.resource_group), None)

class VMScaleSetVMsScenarioTest(CommandTestScript):

    def __init__(self):
        self.resource_group = 'cliTestRg_ScaleSet3'
        self.ss_name = 'scaleset3'
        self.vm_count = 5
        self.instance_ids = ['1', '3', '4', '5', '6']
        self.instance_id_to_delete = 1
        super(VMScaleSetVMsScenarioTest, self).__init__(None, self.test_body, None)

    def _check_vms_power_state(self, expected_power_state):
        for iid in self.instance_ids:
            self.test('vm scaleset-vm get-instance-view --resource-group {} --name {} --instance-id {}'.format(self.resource_group, self.ss_name, iid),
            JMESPathComparator('statuses[1].code', expected_power_state))

    def test_body(self):
        self.test('vm scaleset-vm list --resource-group {} --virtual-machine-scale-set-name {}'.format( #pylint: disable=line-too-long
            self.resource_group, self.ss_name), [
                JMESPathComparator('type(@)', 'array'),
                JMESPathComparator('length(@)', self.vm_count),
                JMESPathComparator("[].name.starts_with(@, '{}')".format(self.ss_name), [True]*self.vm_count),
        ])
        self._check_vms_power_state('PowerState/running')
        


ENV_VAR = {}

TEST_DEF = [
    {
        'test_name': 'vm_usage_list_westus',
        'command': 'vm usage list --location westus --output json'
    },
    {
        'test_name': 'vm_list_from_group',
        'command': 'vm list --resource-group XPLATTESTGEXTENSION9085'
    },
    {
        'test_name': 'vm_list_ip_addresses',
        'command': VMListIPAddressesScenarioTest()
    },
    {
        'test_name': 'vm_images_list_by_aliases',
        'command': VMImageListByAliasesScenarioTest()
    },
    {
        'test_name': 'vm_images_list_thru_services',
        'command': VMImageListThruServiceScenarioTest()
    },
    {
        'test_name': 'vm_size_list',
        'command': VMSizeListScenarioTest()
    },
    {
        'test_name': 'vm_show',
        'command': VMShowScenarioTest()
    },
    {
        'test_name': 'vm_image_list_offers',
        'command': VMImageListOffersScenarioTest()
    },
    {
        'test_name': 'vm_image_list_publishers',
        'command': VMImageListPublishersScenarioTest()
    },
    {
        'test_name': 'vm_image_list_skus',
        'command': VMImageListSkusScenarioTest()
    },
    {
        'test_name': 'vm_image_show',
        'command': VMImageShowScenarioTest()
    },
    {
        'test_name': 'vm_list_sizes',
        'command': VMListSizesScenarioTest()
    },
    {
        'test_name': 'vm_generalize',
        'command': VMGeneralizeScenarioTest()
    },
    {
        'test_name': 'vm_create_state_modifications',
        'command': VMCreateAndStateModificationsScenarioTest()
    },
    {
        'test_name': 'vm_availset',
        'command': VMAvailSetScenarioTest()
    },
    {
        'test_name': 'vm_extension',
        'command': VMExtensionsScenarioTest()
    },
    {
        'test_name': 'vm_machine_extension_image',
        'command': VMMachineExtensionImageScenarioTest()
    },
    {
        'test_name': 'vm_combined_list',
        'command': VMListFoldedScenarioTest()
    },
    {
        'test_name': 'vm_scaleset_gets',
        'command': VMScaleSetGetsScenarioTest()
    },
    {
        'test_name': 'vm_scaleset_states',
        'command': VMScaleSetStatesScenarioTest()
    },
    {
        'test_name': 'vm_scaleset_delete',
        'command': VMScaleSetDeleteScenarioTest()
    },
    {
        'test_name': 'vm_scaleset_vms',
        'command': VMScaleSetVMsScenarioTest()
    },
]


