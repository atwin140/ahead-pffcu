# ODF Client (eqip → acm)

Connects the `eqip` cluster to OpenShift Data Foundation running on the hub
(`acm.sharkbait.tech`, provider service `ocs-provider-server` in
`openshift-storage`) using the `ocs-client-operator` provider/client
architecture. Once the `StorageClient` reaches `Connected`, the client
operator automatically creates local StorageClasses for:

- **Block**: `ocs-storagecluster-ceph-rbd` (RWO/RWOP PVCs)
- **Shared filesystem**: `ocs-storagecluster-cephfs` (RWX PVCs)
- **Object**: `openshift-storage.noobaa.io` (S3 buckets via `ObjectBucketClaim`)

These are driven by the `spec.storageClasses` list on the matching
`StorageConsumer` object on the hub (see below) — the RGW StorageClass name
(`ocs-storagecluster-ceph-rgw`) is **not** supported here ("unsupported
provisioner"); object storage must be requested via the NooBaa OBC
StorageClass name instead.

## Layout

- `base/` — namespace, OperatorGroup, and Subscription for `ocs-client-operator`.
- `overlays/eqip/` — the `StorageClient` CR that onboards this cluster to the hub.

## One-time setup on the hub (not tracked in GitOps)

The provider side requires a `StorageConsumer` object matching the client's
name, created **before** the client can onboard. This isn't managed by this
repo (same as the existing `cluster01`/`cluster02` consumers on the hub —
they're created manually). On the hub:

```bash
export KUBECONFIG=~/acm-kubeconfig
cat <<'EOF' | oc apply -f -
apiVersion: ocs.openshift.io/v1alpha1
kind: StorageConsumer
metadata:
  name: eqip
  namespace: openshift-storage
spec:
  enable: false   # must start disabled - the provider flips this to true on successful onboarding
  storageClasses:
  - name: ocs-storagecluster-ceph-rbd
  - name: ocs-storagecluster-cephfs
  - name: openshift-storage.noobaa.io
EOF
```

Creating it with `enable: false` makes `ocs-operator` auto-generate a real
onboarding ticket in a secret named `onboarding-token-<consumer-uid>` in
`openshift-storage` (valid ~48h). Fetch it and put it in
`overlays/eqip/storageclient.yaml`:

```bash
UID=$(oc get storageconsumer eqip -n openshift-storage -o jsonpath='{.metadata.uid}')
oc get secret onboarding-token-$UID -n openshift-storage -o jsonpath='{.data.onboarding-token}' | base64 -d
```

> Don't hand-craft a ticket with the `onboarding-private-key`/`onboarding-ticket-key`
> secrets - the provider rejects tickets for a consumer unless that
> consumer's own auto-generated ticket secret exists and matches.

## Verifying the connection

```bash
oc get storageclient -n openshift-storage
oc get storageclass | grep -E "ocs-storagecluster|noobaa"
```

`storageclient` should show `PHASE: Connected`. If it's stuck in
`Initializing`:

- `StorageConsumer.ocs.openshift.io "eqip" not found` -> the hub-side
  `StorageConsumer` (above) doesn't exist yet.
- `StorageConsumer already enabled` -> the `StorageConsumer` was created with
  `enable: true` instead of `false`; patch it back to `false` and regenerate
  the ticket.
- Stuck with no errors and no CSV in `openshift-storage` -> check
  `oc get subscription ocs-client-operator -n openshift-storage -o yaml` and
  bundle-unpack pods in `openshift-marketplace`; a transient CDN/registry
  connectivity issue can stall the OLM bundle unpack (delete the failed
  `Job`s in `openshift-marketplace` and recreate the `Subscription` to retry).

## storageProviderEndpoint

Currently pinned to a single hub node IP (`10.0.1.141:31659`, NodePort
`ocs-provider-server`). This isn't HA — if that node goes down, reconnects
will fail until the endpoint is updated. Consider fronting it with a stable
VIP/LoadBalancer on the hub if this becomes a problem.
