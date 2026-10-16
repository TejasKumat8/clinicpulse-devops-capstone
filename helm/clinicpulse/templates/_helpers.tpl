{{/* Base name for every resource: "<release>-clinicpulse", or release name if it already contains "clinicpulse". */}}
{{- define "clinicpulse.fullname" -}}
{{- if contains .Chart.Name .Release.Name -}}
{{- .Release.Name | trunc 50 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 50 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{- define "clinicpulse.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" -}}
{{- end -}}

{{/* Labels shared across all resources */}}
{{- define "clinicpulse.labels" -}}
helm.sh/chart: {{ include "clinicpulse.chart" . }}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: clinicpulse
{{- end -}}

{{/* Selector labels for one component */}}
{{- define "clinicpulse.selectorLabels" -}}
app.kubernetes.io/name: {{ .ctx.Chart.Name }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{- define "clinicpulse.componentLabels" -}}
{{ include "clinicpulse.labels" .ctx }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{/* Image reference helper */}}
{{- define "clinicpulse.image" -}}
{{- printf "%s:%s" .image.repository (default .ctx.Chart.AppVersion .image.tag | toString) -}}
{{- end -}}

{{- define "clinicpulse.backendName" -}}{{ include "clinicpulse.fullname" . }}-backend{{- end -}}
{{- define "clinicpulse.frontendName" -}}{{ include "clinicpulse.fullname" . }}-frontend{{- end -}}
{{- define "clinicpulse.postgresName" -}}{{ include "clinicpulse.fullname" . }}-postgres{{- end -}}
{{- define "clinicpulse.dbSecretName" -}}{{ include "clinicpulse.fullname" . }}-db{{- end -}}

{{/* Database password resolution: explicit > existing secret > generated random */}}
{{- define "clinicpulse.postgresPassword" -}}
{{- if .Values.postgres.auth.password -}}
{{- .Values.postgres.auth.password -}}
{{- else -}}
{{- $existing := lookup "v1" "Secret" .Release.Namespace (include "clinicpulse.dbSecretName" .) -}}
{{- if and $existing $existing.data (index $existing.data "postgres-password") -}}
{{- index $existing.data "postgres-password" | b64dec -}}
{{- else -}}
{{- randAlphaNum 24 -}}
{{- end -}}
{{- end -}}
{{- end -}}
