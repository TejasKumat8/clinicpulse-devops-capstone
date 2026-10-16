# AWS provider configuration using default credential chain (aws configure, SSO, or environment variables)
provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.tags
  }
}

data "aws_availability_zones" "available" {
  count = length(var.availability_zones) == 0 ? 1 : 0

  state = "available"

  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}

locals {
  azs = slice(
    length(var.availability_zones) > 0 ? var.availability_zones : data.aws_availability_zones.available[0].names,
    0, var.az_count
  )

  tags = {
    Project     = var.project_name
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}
