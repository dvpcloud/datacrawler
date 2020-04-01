import glob
import filecmp
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.mail import MailSender

class EmailOnChange(object):

    def __init__(self,destination, mailer):
        self.destination = destination
        self.mailer = mailer
    
    @classmethod
    def from_crawler(cls,crawler):
        if not crawler.settings.getbool("EMAIL_ON_CHANGE_ENABLED"):
            raise NotConfigured
        if not crawler.settings.get("EMAIL_ON_CHANGE_DESTINATION"):
            raise NotConfigured("EMAIL_ON_CHANGE_DESTINATION must be provided")

        mailer = MailSender.from_settings(crawler.settings)
        destination = crawler.settings.get("EMAIL_ON_CHANGE_DESTINATION")
        
        extension = cls(destination, mailer)

        crawler.signals.connect(extension.engine_stopped,signal=signals.engine_stopped)

        return extension

    def engine_stopped(self):
        #print("\n\n\n EXTENSION WAS RUN \n\n\n")
        runs = sorted(glob.glob("/tmp/[0-9]*-[0-9]*-[0-9]*T[0-9]*-[0-9]*-[0-9]*.json"), reverse=True)

        if len(runs) < 2:
            return
        current_file,previous_file = runs[0:2]

        if not filecmp.cmp(current_file,previous_file):
            print("\n\n\n The files are different \n\n\n")
            with open (current_file) as f:
                self.mailer.send(
                    to=[self.destination],
                    subject="dataset changed",
                    body="changes in datasets detected, see attachment",
                    attachs=[(current_file.split('/')[-1], 'application/json',f)]
                )
        else:
            print("\n\n\n no change \n\n\n")

