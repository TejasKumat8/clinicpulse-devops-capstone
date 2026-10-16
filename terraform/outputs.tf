output "region" {
  description = "Target AWS region."
  value       = var.aws_region
}

output "vpc_id" {
  description = "VPC identifier."
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs for ingress load balancers."
  value       = module.vpc.public_subnets
}

output "private_subnet_ids" {
  description = "Private subnet IDs hosting EKS worker nodes."
  value       = module.vpc.private_subnets
}

output "cluster_name" {
  description = "EKS cluster identifier."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "Kubernetes API endpoint."
  value       = module.eks.cluster_endpoint
}

output "cluster_version" {
  description = "Kubernetes control plane version."
  value       = module.eks.cluster_version
}

output "node_group_names" {
  description = "Names of provisioned managed node groups."
  value       = keys(module.eks.eks_managed_node_groups)
}

output "configure_kubectl" {
  description = "CLI command to update local kubeconfig context."
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

output "github_actions_role_arn" {
  description = "IAM Role ARN to be configured in GitHub repository variable AWS_DEPLOY_ROLE_ARN."
  value       = local.github_enabled ? aws_iam_role.github_actions[0].arn : null
}
