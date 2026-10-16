terraform {
  required_version = ">= 1.9.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # Local state for development & evaluation environment (git-ignored)
  # In enterprise production environments, migrate to remote S3 backend with state locking:
  #
  # backend "s3" {
  #   bucket       = "clinicpulse-terraform-state-<account-id>"
  #   key          = "eks/terraform.tfstate"
  #   region       = "ap-south-1"
  #   use_lockfile = true
  #   encrypt      = true
  # }
}
