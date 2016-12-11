'Data models for NCBI downloader'
import logging

class DownloadJob:
    def __init__(self, accession, callback_id, email, filename, molecule_type):
        self.accession = accession
        self.callback_id = callback_id
        self.email = email
        self.filename = filename
        self.molecule_type = molecule_type

    @classmethod
    def from_dict(cls, data):
        accession = data.get("accession", None)
        callback_id = data.get("callback_id", None)
        email = data.get("email", None)
        filename = data.get("filename", None)
        molecule_type = data.get("molecule_type", None)
        if molecule_type not in ("protein", "nucleotide"):
            logging.debug("Ignoring invalid molecule_type %r, using 'nucleotide' instead", molecule_type)
            molecule_type = "nucleotide"
        return cls(accession, callback_id, email, filename, molecule_type)

    def to_dict(self):
        ret = {}
        if self.accession is not None:
            ret['accession'] = self.accession
        if self.callback_id is not None:
            ret['callback_id'] = self.callback_id
        if self.email is not None:
            ret['email'] = self.email
        if self.filename is not None:
            ret['filename'] = self.filename
        if self.molecule_type is not None:
            ret['molecule_type'] = self.molecule_type

        return ret

    def __str__(self):
        return "DownloadJob(accession:{j.accession}, callback_id:{j.callback_id}, email:{j.email}, filename:{j.filename}, molecule_type:{j.molecule_type})".format(j=self)

    def __repr__(self):
        return str(self)
