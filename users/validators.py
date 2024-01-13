import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import PhoneNumberFormat, NumberParseException
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def validate_international_phone_number(value):
    try:
        logger.debug(f"Original phone number: {value}")

        # Normalize the phone number by removing spaces and other non-digit characters, except the leading '+'
        normalized_number = '+' + ''.join(filter(str.isdigit, value[1:]))
        logger.debug(f"Normalized phone number: {normalized_number}")

        # Parse the normalized phone number using phonenumbers
        parsed_number = phonenumbers.parse(normalized_number, None)
        logger.debug(f"Parsed phone number: {parsed_number}")

        # Check if the parsed number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(f'Invalid phone number: {value}')

        # Format the phone number in E.164 format (e.g., +1234567890)
        formatted_number = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
        logger.debug(f"Formatted phone number: {formatted_number}")

        return formatted_number

    except NumberParseException as e:
        logger.error(f"NumberParseException: Invalid phone number format for {value}. Error: {e}")
        raise ValidationError(f'Invalid phone number format: {value}. Error: {e}')
    except Exception as e:
        logger.error(f"Exception: {str(e)} for phone number: {value}")
        raise ValidationError(str(e))