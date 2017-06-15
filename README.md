---
services: storage
platforms: python
author: lmazuel
---

# Getting Started with Azure Storage Resource Provider in Python

This sample shows how to manage your storage account using the Azure Storage Resource Provider for Python. The Storage Resource Provider is a client library for working with the storage accounts in your Azure subscription. Using the client library, you can create a new storage account, read its properties, list all storage accounts in a given subscription or resource group, read and regenerate the storage account keys, and delete a storage account.  


**On this page**

- [Run this sample](#run)
- [What is example.py doing?](#example)
    - [Check storage account name availability](#check-available)
    - [Create a new storage account](#create-account)
    - [Get the properties of an account](#get-properties)
    - [List storage accounts](#list-storage-accounts)
    - [List storage accounts by resource group](#list-storage-accounts-rg)
    - [Get the storage account keys](#get-keys)
    - [Regenerate a storage account key](#regenerate-keys)
    - [Modify the storage account SKU](#update-storage-account)
    - [Delete a storage account](#delete-account)
    - [Usage](#usage)
- [More information](#more-info)

<a name="run"></a>
## Run this sample

1. If you don't already have it, [install Python](https://www.python.org/downloads/).

2. We recommend using a [virtual environment](https://docs.python.org/3/tutorial/venv.html) to run this example, but it's not mandatory. You can initialize a virtual environment this way:

    ```
    pip install virtualenv
    virtualenv mytestenv
    cd mytestenv
    source bin/activate
    ```

3. Clone the repository.

    ```
    git clone https://github.com/Azure-Samples/storage-python-manage.git
    ```

4. Install the dependencies using pip.

    ```
    cd storage-python-manage
    pip install -r requirements.txt
    ```

5. Create an Azure service principal, using 
[Azure CLI](http://azure.microsoft.com/documentation/articles/resource-group-authenticate-service-principal-cli/),
[PowerShell](http://azure.microsoft.com/documentation/articles/resource-group-authenticate-service-principal/)
or [Azure Portal](http://azure.microsoft.com/documentation/articles/resource-group-create-service-principal-portal/).

6. Export these environment variables into your current shell. 

    ```
    export AZURE_TENANT_ID={your tenant id}
    export AZURE_CLIENT_ID={your client id}
    export AZURE_CLIENT_SECRET={your client secret}
    export AZURE_SUBSCRIPTION_ID={your subscription id}
    ```

7. Run the sample.

    ```
    python example.py
    ```

<a id="example"></a>
## What is example.py doing?

The sample walks you through several Storage Resource Provider operations. It starts by setting up a ResourceManagementClient and StorageManagementClient objects using your subscription and credentials.

```python
import os
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters

subscription_id = os.environ.get(
    'AZURE_SUBSCRIPTION_ID',
    '11111111-1111-1111-1111-111111111111') # your Azure Subscription Id
credentials = ServicePrincipalCredentials(
    client_id=os.environ['AZURE_CLIENT_ID'],
    secret=os.environ['AZURE_CLIENT_SECRET'],
    tenant=os.environ['AZURE_TENANT_ID']
)
resource_client = ResourceManagementClient(credentials, subscription_id)
storage_client = StorageManagementClient(credentials, subscription_id)
```

It also sets up a ResourceGroup object (resource_group_params) to be used as a parameter in some of the API calls.

```python
resource_group_params = {'location':'westus'}
```

There are a couple of supporting functions (`print_item` and `print_properties`) that print an Azure object and its properties.

<a name="check-available"></a>
### Check storage account name availability

Check the availability and/or the validity of a given string as a storage account.

```python
bad_account_name = 'invalid-or-used-name'
availability = storage_client.storage_accounts.check_name_availability(bad_account_name)
print('The account {} is available: {}'.format(bad_account_name, availability.name_available))
print('Reason: {}'.format(availability.reason))
print('Detailed message: {}'.format(availability.message))
```

<a name="create-account"></a>
### Create a new storage account

```python
storage_async_operation = storage_client.storage_accounts.create(
    GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    StorageAccountCreateParameters(
        sku=Sku(SkuName.standard_ragrs),
        kind=Kind.storage,
        location='westus'
    )
)
storage_account = storage_async_operation.result()
```

<a name="get-properties"></a>
### Get the properties of a storage account

```python
storage_account = storage_client.storage_accounts.get_properties(
    GROUP_NAME, STORAGE_ACCOUNT_NAME)
```

<a name="list-storage-accounts"></a>
### List storage accounts

```python
for item in storage_client.storage_accounts.list():
    print_item(item)
```

<a name="list-storage-accounts-rf"></a>
### List storage accounts by resource group

```python
for item in storage_client.storage_accounts.list_by_resource_group(GROUP_NAME):
    print_item(item)
```

<a name="get-keys"></a>
### Get the storage account keys

```python
storage_keys = storage_client.storage_accounts.list_keys(GROUP_NAME, STORAGE_ACCOUNT_NAME)
storage_keys = {v.key_name: v.value for v in storage_keys.keys}
print('\tKey 1: {}'.format(storage_keys['key1']))
print('\tKey 2: {}'.format(storage_keys['key2']))
```

<a name="regenerate-keys"></a>
### Regenerate a storage account key

```python
storage_keys = storage_client.storage_accounts.regenerate_key(
    GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    'key1')
storage_keys = {v.key_name: v.value for v in storage_keys.keys}
print('\tNew key 1: {}'.format(storage_keys['key1']))
```

<a name="update-storage-account"></a>
### Modify the storage account SKU

The storage account SKU specifies what type of replication applies to the storage account. You can update the storage account SKU to change how the storage account is replicated, as shown in the sample:

```python
storage_account = storage_client.storage_accounts.update(
    GROUP_NAME, STORAGE_ACCOUNT_NAME,
    StorageAccountUpdateParameters(
        sku=Sku(SkuName.standard_grs)
    )
)
```

Note that modifying the SKU for a production storage account may have associated costs. For example, if you convert a locally redundant storage account to a geo-redundant storage account, you will be charged for replicating your data to the secondary region. Before you modify the SKU for a production account, be sure to consider any cost implications. See [Azure Storage replication](https://azure.microsoft.com/documentation/articles/storage-redundancy/) for additional information about storage replication.


<a name="delete-account"></a>
### Delete a storage account

```python
storage_client.storage_accounts.delete(GROUP_NAME, STORAGE_ACCOUNT_NAME)
```

<a name="usage"></a>
### List usage

```python
for usage in storage_client.usage.list():
    print('\t{}'.format(usage.name.value))
```

<a name="more-info"></a>
## More information

- [Azure SDK for Python](http://github.com/Azure/azure-sdk-for-python) 
- [Azure Storage Documentation](https://azure.microsoft.com/services/storage/)
