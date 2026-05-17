{{/*
Chart name (sanitized).
*/}}
{{- define "video-streaming.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Fully-qualified app name. If `fullnameOverride` is set, use it verbatim.
Otherwise: `<release>-<chartname>` unless release already contains the chart
name (avoid release-name-name-name duplication).
*/}}
{{- define "video-streaming.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "video-streaming.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Canonical Kubernetes labels. `component` is set by the caller via dict.
Call with: {{- include "video-streaming.labels" (dict "ctx" . "component" "backend") | nindent 4 }}
*/}}
{{- define "video-streaming.labels" -}}
helm.sh/chart: {{ include "video-streaming.chart" .ctx }}
{{ include "video-streaming.selectorLabels" . }}
{{- if .ctx.Chart.AppVersion }}
app.kubernetes.io/version: {{ .ctx.Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .ctx.Release.Service }}
{{- end -}}

{{- define "video-streaming.selectorLabels" -}}
app.kubernetes.io/name: {{ include "video-streaming.name" .ctx }}
app.kubernetes.io/instance: {{ .ctx.Release.Name }}
{{- with .component }}
app.kubernetes.io/component: {{ . }}
{{- end }}
{{- end -}}

{{/*
ServiceAccount name to use on pods.
*/}}
{{- define "video-streaming.serviceAccountName" -}}
{{- if .Values.serviceAccount.create -}}
{{- default (include "video-streaming.fullname" .) .Values.serviceAccount.name -}}
{{- else -}}
{{- default "default" .Values.serviceAccount.name -}}
{{- end -}}
{{- end -}}

{{/*
Name of the shared ConfigMap and Secret.
*/}}
{{- define "video-streaming.configMapName" -}}
{{ include "video-streaming.fullname" . }}-config
{{- end -}}

{{- define "video-streaming.secretName" -}}
{{- if .Values.secret.existingSecret -}}
{{- .Values.secret.existingSecret -}}
{{- else -}}
{{ include "video-streaming.fullname" . }}-secret
{{- end -}}
{{- end -}}

{{/*
Build a fully-qualified image reference for a service component.
Call with: {{ include "video-streaming.image" (dict "ctx" . "svc" .Values.backend) }}
*/}}
{{- define "video-streaming.image" -}}
{{- $tag := default .ctx.Chart.AppVersion .ctx.Values.image.tag -}}
{{- $tag = default $tag .svc.image.tag -}}
{{- printf "%s/%s:%s" .ctx.Values.image.registry .svc.image.repository $tag -}}
{{- end -}}

{{/*
Pod / container security contexts — non-root, drop everything.
*/}}
{{- define "video-streaming.podSecurityContext" -}}
runAsNonRoot: true
runAsUser: 1000
runAsGroup: 1000
fsGroup: 1000
seccompProfile:
  type: RuntimeDefault
{{- end -}}

{{- define "video-streaming.containerSecurityContext" -}}
allowPrivilegeEscalation: false
capabilities:
  drop: [ "ALL" ]
readOnlyRootFilesystem: false
{{- end -}}
