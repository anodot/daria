from agent.modules import db
from agent.modules.logger import get_logger
from agent import streamsets

logger = get_logger(__name__)

streamsets_ = streamsets.repository.get_all()
if len(streamsets_) == 1:
    logger.info(f'You have only one streamsets instance, can\'t balance')
    exit(0)
elif len(streamsets_) == 1:
    logger.info(f'You don\'t have any streamsets instances, can\'t balance')
    exit(0)


balancer = streamsets.manager.StreamsetsBalancer()
balancer.balance()
# todo this is temporary
db.session().commit()
db.session().close()
