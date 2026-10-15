OpenShift 101 demonstration materials

Use with the Instructor and Companion Guide. These examples have not been
executed against your cluster. Rehearse them before class.

app-example.yaml is a teaching skeleton. Replace the image placeholder with
the approved digest of an image that serves HTTP / on port 8080 and runs under
the actual cluster SCC. Verify requested resources suit the chosen image.
Create the ocp101 project first. Confirm policy permits router access.
The Route uses edge TLS: client-to-router traffic uses TLS, backend HTTP does not.

default-deny-ingress.yaml is intended only for the empty ocp101-policy namespace.
Do not apply it in a namespace with production workloads. The ACM demo uses an
inform-only ConfigurationPolicy checking for this resource and targets one
training managed cluster. Placement and hub policy objects are prepared in the
ACM console because the actual cluster labels and cluster set are site-specific.

For the failed-pod demo, copy the Deployment as web-broken and change BOTH its
selector and pod labels to app=web-broken. Use a deliberately nonexistent tag in
the approved repository. Repair its image reference in the Deployment.

No credentials or real environment identifiers belong in this package.
