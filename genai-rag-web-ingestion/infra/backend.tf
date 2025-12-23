terraform {
  backend "azurerm" {
    resource_group_name  = "azure_rag"
    storage_account_name = "ragstorageaccountjj"
    container_name       = "tfstate"
    key                  = "rag/prod/terraform.tfstate"
  }
}
