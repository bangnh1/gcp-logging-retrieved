from main import queryStatementTransform


def test_transform():
    statement = 'resource.type="k8s_container"    resource.labels.cluster_name="dev-test-gke-cluster"'
    assert queryStatementTransform(
        statement) == 'resource.type:"k8s_container" AND resource.labels.cluster_name:"dev-test-gke-cluster"'
