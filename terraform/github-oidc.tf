# Keyless GitHub Actions CI/CD Deployment using AWS IAM OIDC Federation.
# Eliminates long-lived access keys by exchanging ephemeral JWT tokens for temporary STS credentials.

locals {
  github_enabled  = var.github_repository != ""
  github_oidc_url = "token.actions.githubusercontent.com"
  github_oidc_provider_arn = local.github_enabled ? (
    var.create_github_oidc_provider
    ? aws_iam_openid_connect_provider.github[0].arn
    : "arn:aws:iam::${data.aws_caller_identity.current.account_id}:oidc-provider/${local.github_oidc_url}"
  ) : ""
  cluster_arn = "arn:aws:eks:${var.aws_region}:${data.aws_caller_identity.current.account_id}:cluster/${var.cluster_name}"
}

resource "aws_iam_openid_connect_provider" "github" {
  count = local.github_enabled && var.create_github_oidc_provider ? 1 : 0

  url            = "https://${local.github_oidc_url}"
  client_id_list = ["sts.amazonaws.com"]
}

data "aws_iam_policy_document" "github_assume_role" {
  count = local.github_enabled ? 1 : 0

  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [local.github_oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.github_oidc_url}:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "${local.github_oidc_url}:sub"
      values = [
        "repo:${var.github_repository}:ref:refs/heads/main",
        "repo:${var.github_repository}:environment:production",
      ]
    }
  }
}

resource "aws_iam_role" "github_actions" {
  count = local.github_enabled ? 1 : 0

  name                 = "${var.project_name}-github-actions-deploy"
  description          = "Assumed by GitHub Actions (${var.github_repository}) to deploy ClinicPulse via Helm"
  assume_role_policy   = data.aws_iam_policy_document.github_assume_role[0].json
  max_session_duration = 3600
}

data "aws_iam_policy_document" "github_eks" {
  count = local.github_enabled ? 1 : 0

  statement {
    actions   = ["eks:DescribeCluster"]
    resources = [local.cluster_arn]
  }
}

resource "aws_iam_role_policy" "github_eks" {
  count = local.github_enabled ? 1 : 0

  name   = "eks-describe-cluster"
  role   = aws_iam_role.github_actions[0].id
  policy = data.aws_iam_policy_document.github_eks[0].json
}
