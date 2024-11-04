import random
import string
import time
from datetime import datetime
from typing import List, Optional

import requests
from django.http import HttpResponse
from django.template.loader import render_to_string

import researchhub.settings as settings
from paper.models import Paper
from researchhub_document.models import ResearchhubPost
from user.models import Author


# Class for handling Digital Object Identifier (DOI) generation and registration with Crossref.
class DOI:
    def __init__(
        self, base_doi: Optional[str] = None, version: Optional[int] = None
    ) -> None:
        self.base_doi = base_doi
        if base_doi is None:
            self.base_doi = self._generate_base_doi()

        self.doi = self.base_doi
        if version is not None:
            self.doi = f"{self.base_doi}.{version}"

    # Generate a random DOI using the configured prefix ("10.55277/ResearchHub.") and a random suffix.
    def _generate_base_doi(self) -> str:
        return settings.CROSSREF_DOI_PREFIX + "".join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(settings.CROSSREF_DOI_SUFFIX_LENGTH)
        )

    # Register DOI for a ResearchHub post.
    def register_doi_for_post(
        self, authors: List[Author], title: str, rh_post: ResearchhubPost
    ) -> HttpResponse:
        url = f"{settings.BASE_FRONTEND_URL}/post/{rh_post.id}/{rh_post.slug}"
        return self.register_doi(authors, title, url)

    # Register DOI for a ResearchHub paper.
    def register_doi_for_paper(
        self, authors: List[Author], title: str, rh_paper: Paper
    ) -> HttpResponse:
        url = f"{settings.BASE_FRONTEND_URL}/paper/{rh_paper.id}/{rh_paper.slug}"
        return self.register_doi(authors, title, url)

    # Main method to register a DOI with Crossref.
    def register_doi(self, authors: List[Author], title: str, url: str) -> HttpResponse:
        dt = datetime.today()
        contributors = []

        for author in authors:
            institution = None
            if author.university:
                place = None
                if author.university.city:
                    place = f"{author.university.city}, {author.university.state}"
                institution = {
                    "name": author.university.name,
                    "place": place,
                }

            contributors.append(
                {
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                    "orcid": author.orcid_id,
                    "institution": institution,
                }
            )

        context = {
            "timestamp": int(time.time()),
            "contributors": contributors,
            "title": title,
            "publication_month": dt.month,
            "publication_day": dt.day,
            "publication_year": dt.year,
            "doi": self.base_doi,
            "url": url,
        }
        crossref_xml = render_to_string("crossref.xml", context)
        files = {
            "operation": (None, "doMDUpload"),
            "login_id": (None, settings.CROSSREF_LOGIN_ID),
            "login_passwd": (None, settings.CROSSREF_LOGIN_PASSWORD),
            "fname": ("crossref.xml", crossref_xml),
        }
        crossref_response = requests.post(settings.CROSSREF_API_URL, files=files)
        return crossref_response
