resource "azurerm_resource_group" "rag_example" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "example" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rag_example.name
  location                 = azurerm_resource_group.rag_example.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  tags = {
    environment = "staging"
  }
}

resource "azurerm_search_service" "aisearch" {
  name                = var.aisearchname
  resource_group_name = azurerm_resource_group.rag_example.name
  location            = azurerm_resource_group.rag_example.location
  sku                 = "free"

  local_authentication_enabled = false
}

resource "azurerm_cognitive_account" "example" {
  name                = var.cognitiveaccountname
  location            = azurerm_resource_group.rag_example.location
  resource_group_name = azurerm_resource_group.rag_example.name
  kind                = "OpenAI"
  sku_name            = "S0"
}

resource "azurerm_cognitive_deployment" "example" {
  name                 = var.deploymentname
  cognitive_account_id = azurerm_cognitive_account.example.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-3-large"
    version = "1"
  }

  sku {
    name = "Standard"
  }
}
