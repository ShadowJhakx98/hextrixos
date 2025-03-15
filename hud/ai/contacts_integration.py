import os
import json
import logging
import base64

from google_api_manager import GoogleAPIManager

logger = logging.getLogger(__name__)

class ContactsIntegration:
    def __init__(self, api_manager):
        self.api_manager = api_manager
        # No need to authenticate here, the api_manager already handles that
        self.initialize()

    def initialize(self):
        """Initialize the People API service."""
        try:
            self.contacts_service = self.api_manager.get_service('people', 'v1')
            return True
        except Exception as e:
            logger.error(f"Failed to initialize People API service: {e}")
            return False

    def _process_contact(self, person, detailed=False):
        """Process a contact from the API into a simplified dictionary."""
        contact = {
            'resource_name': person.get('resourceName', ''),
            'display_name': ''
        }

        if 'names' in person and person['names']:
            name = person['names'][0]
            contact['display_name'] = name.get('displayName', 'Unnamed')

        if 'emailAddresses' in person and person['emailAddresses']:
            for email in person['emailAddresses']:
                if email.get('metadata', {}).get('primary', False):
                    contact['primary_email'] = email.get('value', '')
                    break
            else:
                contact['primary_email'] = person['emailAddresses'][0].get('value', '')

        if 'phoneNumbers' in person and person['phoneNumbers']:
            for phone in person['phoneNumbers']:
                if phone.get('metadata', {}).get('primary', False):
                    contact['primary_phone'] = phone.get('value', '')
                    break
            else:
                contact['primary_phone'] = person['phoneNumbers'][0].get('value', '')

        if 'photos' in person and person['photos']:
            for photo in person['photos']:
                if photo.get('metadata', {}).get('primary', False):
                    contact['photo_url'] = photo.get('url', '')
                    break

        if detailed:
            if 'addresses' in person and person['addresses']:
                contact['addresses'] = [{'type': addr.get('type', ''), 'value': addr.get('formattedValue', '')} 
                                        for addr in person['addresses']]
            if 'organizations' in person and person['organizations']:
                contact['organization'] = person['organizations'][0].get('name', '')
            if 'biographies' in person and person['biographies']:
                for bio in person['biographies']:
                    bio_value = bio.get('value', '')
                    if bio_value:
                        contact['biography'] = bio_value
                        break

        return contact

    def get_contacts(self, max_results=100):
        """Fetch all contacts from Google Contacts."""
        try:
            if not self.contacts_service:
                if not self.initialize():
                    return []
            contacts = []
            page_token = None
            while True:
                results = self.contacts_service.people().connections().list(
                    resourceName='people/me',
                    pageSize=max_results,
                    personFields='names,emailAddresses,phoneNumbers,photos,addresses,organizations,biographies',
                    pageToken=page_token
                ).execute()
                connections = results.get('connections', [])
                for person in connections:
                    contact = self._process_contact(person, detailed=True)
                    if contact:
                        contacts.append(contact)
                page_token = results.get('nextPageToken')
                if not page_token or len(contacts) >= max_results:
                    break
            return contacts
        except Exception as e:
            logger.error(f"Error fetching contacts: {e}")
            return []

    def search_contacts(self, query):
        """Search contacts using the Google People API."""
        try:
            if not self.contacts_service:
                if not self.initialize():
                    return []
            results = self.contacts_service.people().searchContacts(
                query=query,
                readMask='names,emailAddresses,phoneNumbers,photos,organizations,addresses,biographies'
            ).execute()
            contacts = []
            if 'results' in results:
                for result in results['results']:
                    person = result['person']
                    contact = self._process_contact(person, detailed=True)
                    if contact:
                        contacts.append(contact)
            return contacts
        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            return []

    def update_contact(self, resource_name, contact_data):
        """Update an existing contact."""
        try:
            person = {
                'names': [{'givenName': contact_data.get('given_name', ''),
                           'familyName': contact_data.get('family_name', '')}],
                'emailAddresses': [{'value': contact_data.get('email', '')}],
                'phoneNumbers': [{'value': contact_data.get('phone', '')}],
                'addresses': [{'formattedValue': contact_data.get('address', '')}],
                'organizations': [{'name': contact_data.get('organization', '')}],
                'biographies': [{'value': contact_data.get('biography', '')}]
            }
            update_fields = 'names,emailAddresses,phoneNumbers,addresses,organizations,biographies'
            updated_person = self.contacts_service.people().updateContact(
                resourceName=resource_name,
                updatePersonFields=update_fields,
                body=person
            ).execute()
            return self._process_contact(updated_person, detailed=True)
        except Exception as e:
            logger.error(f"Error updating contact: {e}")
            return None

    def create_contact(self, contact_data):
        """Create a new contact."""
        try:
            person = {
                'names': [{'givenName': contact_data.get('given_name', ''),
                           'familyName': contact_data.get('family_name', '')}],
                'emailAddresses': [{'value': contact_data.get('email', '')}],
                'phoneNumbers': [{'value': contact_data.get('phone', '')}],
                'addresses': [{'formattedValue': contact_data.get('address', '')}],
                'organizations': [{'name': contact_data.get('organization', '')}],
                'biographies': [{'value': contact_data.get('biography', '')}]
            }
            created_person = self.contacts_service.people().createContact(
                body=person,
                personFields='names,emailAddresses,phoneNumbers,addresses,organizations,biographies'
            ).execute()
            return self._process_contact(created_person, detailed=True)
        except Exception as e:
            logger.error(f"Error creating contact: {e}")
            return None

    def delete_contact(self, resource_name):
        """Delete a contact by resource name."""
        try:
            self.contacts_service.people().deleteContact(resourceName=resource_name).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting contact: {e}")
            return False

    def update_contact_photo(self, resource_name, photo_path):
        """Update a contact's photo."""
        try:
            with open(photo_path, 'rb') as photo_file:
                photo_bytes = base64.b64encode(photo_file.read()).decode('utf-8')
            self.contacts_service.people().updateContactPhoto(
                resourceName=resource_name,
                body={'photoBytes': photo_bytes}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error updating contact photo: {e}")
            return False