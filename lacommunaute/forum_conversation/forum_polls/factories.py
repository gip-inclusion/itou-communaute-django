from machina.test.factories.polls import (
    TopicPollFactory as BaseTopicPollFactory,
    TopicPollOptionFactory as BaseTopicPollOptionFactory,
    TopicPollVoteFactory as BaseTopicPollVoteFactory,
)


class TopicPollFactory(BaseTopicPollFactory):
    pass


class TopicPollOptionFactory(BaseTopicPollOptionFactory):
    pass


class TopicPollVoteFactory(BaseTopicPollVoteFactory):
    pass
