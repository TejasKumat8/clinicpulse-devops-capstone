# ClinicPulse Cloud Infrastructure (Terraform)

Provisions a production-grade AWS foundation for ClinicPulse:
- **Dedicated VPC**: Dual Availability Zones (`ap-south-1a`, `ap-south-1b`), CIDR `10.40.0.0/16`.
- **Subnets**: 2 Public Subnets (NAT Gateway + Internet Gateway) and 2 Private Subnets (EKS compute).
- **Amazon EKS**: Managed Kubernetes cluster (`clinicpulse-eks`) with Amazon Linux 2023 worker nodes.
- **Add-ons**: VPC CNI, CoreDNS, Kube-Proxy, AWS EBS CSI driver (for persistent volume storage), and Pod Identity Agent.
- **OIDC IAM Role**: Keyless deployment federation for GitHub Actions (`AWS_DEPLOY_ROLE_ARN`).

## Usage

```bash
# 1. Initialize Terraform plugins
terraform init

# 2. Format and validate syntax
terraform fmt -check
terraform validate

# 3. Create execution plan
terraform plan -out=tfplan

# 4. Provision infrastructure
terraform apply tfplan

# 5. Connect kubectl to cluster
aws eks update-kubeconfig --region ap-south-1 --name clinicpulse-eks
```

## Safe Teardown

```bash
# Delete Kubernetes ingress and EBS volumes first, then destroy cloud resources:
cd ..
./scripts/teardown-aws.sh
```
