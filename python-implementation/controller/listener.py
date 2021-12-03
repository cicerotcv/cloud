

class Listener():
    def __init__(self, load_balancer) -> None:
        self.load_balancer = load_balancer
        self.client = self.load_balancer.client
        self.name = 'listener-' + self.load_balancer.region_name
        self.ARN = None

    def create(self):
        lb_arn = self.load_balancer.ARN
        tg_arn = self.load_balancer.target_group.ARN
        create = self.client.create_listener

        response = create(
            LoadBalancerArn=lb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[{'Type': 'forward', 'TargetGroupArn': tg_arn}])

        listeners = response["Listeners"]
        listener = listeners[0]
        self.ARN = listener['ListenerArn']

    def delete(self):
        self.client.delete_listener(ListenerArn=self.ARN)
