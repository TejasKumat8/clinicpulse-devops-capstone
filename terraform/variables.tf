variable "aws_region" {
  description = "AWS region for all infrastructure resources."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project identifier used for resource naming and tagging."
  type        = string
  default     = "clinicpulse"
}

variable "environment" {
  description = "Environment identifier tag (e.g. dev, staging, prod)."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner tag for resource provenance and attribution."
  type        = string
  default     = "tejas-kumat"
}

# ---------- Network ----------
variable "vpc_cidr" {
  description = "CIDR block for the dedicated ClinicPulse VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "az_count" {
  description = "Number of Availability Zones to span."
  type        = number
  default     = 2

  validation {
    condition     = var.az_count >= 2 && var.az_count <= 3
    error_message = "EKS requires subnets in at least two availability zones."
  }
}

variable "availability_zones" {
  description = "Explicit list of availability zones. Empty defaults to dynamic lookup."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.availability_zones) == 0 || length(var.availability_zones) >= 2
    error_message = "Provide at least two availability zones or leave empty for lookup."
  }
}

# ---------- EKS ----------
variable "cluster_name" {
  description = "Name of the Amazon EKS cluster."
  type        = string
  default     = "clinicpulse-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes control plane version."
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "EC2 instance types for the EKS managed node group."
  type        = list(string)
  default     = ["t3.large"]
}

variable "node_min_size" {
  description = "Minimum size of the managed node group."
  type        = number
  default     = 2
}

variable "node_desired_size" {
  description = "Desired capacity of the managed node group."
  type        = number
  default     = 2
}

variable "node_max_size" {
  description = "Maximum size of the managed node group for autoscaling."
  type        = number
  default     = 4
}

# ---------- CI/CD Integration ----------
variable "github_repository" {
  description = "GitHub repository in format owner/repo allowed to deploy via OIDC."
  type        = string
  default     = ""
}

variable "create_github_oidc_provider" {
  description = "Set to true if AWS account needs the token.actions.githubusercontent.com provider created."
  type        = bool
  default     = true
}
