import re
import logging
from datetime import datetime
from typing import Dict, List, Tuple


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self):
        """Initialize the data validator"""
        self.validation_results = []

    def validate_extracted_data(self, data: Dict) -> Dict:
        """
        Validate the extracted data and return validation results

        Args:
            data: Extracted data dictionary

        Returns:
            dict: Validation results with scores and issues
        """
        self.validation_results = []
        logger.info("Starting data validation")
        # Validate each field type
        self._validate_personal_info(data)
        self._validate_dates(data)
        self._validate_contact_info(data)
        self._validate_accident_info(data)

        # Calculate overall score
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for result in self.validation_results if result['valid'])
        overall_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        logger.info(f"Validation completed - Overall score: {overall_score}%, Passed: {passed_checks}/{total_checks}")
        return {
            "overall_score": round(overall_score, 2),
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "validation_details": self.validation_results,
            "completeness_score": self._calculate_completeness(data),
            "summary": self._generate_summary()
        }

    def _validate_personal_info(self, data: Dict):
        """Validate personal information fields"""
        # ID Number validation (Israeli ID format)
        id_number = data.get('idNumber', '')
        if id_number:
            is_valid_id = self._validate_israeli_id(id_number)
            self.validation_results.append({
                'field': 'idNumber',
                'value': id_number,
                'valid': is_valid_id,
                'message': 'Valid Israeli ID format' if is_valid_id else 'Invalid Israeli ID format'
            })

        # Name validation
        first_name = data.get('firstName', '')
        last_name = data.get('lastName', '')

        self.validation_results.append({
            'field': 'firstName',
            'value': first_name,
            'valid': len(first_name.strip()) > 0,
            'message': 'First name provided' if first_name.strip() else 'First name missing'
        })

        self.validation_results.append({
            'field': 'lastName',
            'value': last_name,
            'valid': len(last_name.strip()) > 0,
            'message': 'Last name provided' if last_name.strip() else 'Last name missing'
        })

        # Gender validation
        gender = data.get('gender', '')
        valid_genders = ['זכר', 'נקבה', 'male', 'female', 'M', 'F', 'ז', 'נ']
        is_valid_gender = gender.strip() in valid_genders

        self.validation_results.append({
            'field': 'gender',
            'value': gender,
            'valid': is_valid_gender,
            'message': 'Valid gender value' if is_valid_gender else 'Invalid or missing gender'
        })

    def _validate_dates(self, data: Dict):
        """Validate date fields"""
        date_fields = [
            ('dateOfBirth', 'Date of birth'),
            ('dateOfInjury', 'Date of injury'),
            ('formFillingDate', 'Form filling date'),
            ('formReceiptDateAtClinic', 'Form receipt date')
        ]

        for field_name, field_label in date_fields:
            date_obj = data.get(field_name, {})
            if isinstance(date_obj, dict):
                is_valid, message = self._validate_date_object(date_obj)
                self.validation_results.append({
                    'field': field_name,
                    'value': f"{date_obj.get('day', '')}/{date_obj.get('month', '')}/{date_obj.get('year', '')}",
                    'valid': is_valid,
                    'message': f'{field_label}: {message}'
                })

    def _validate_contact_info(self, data: Dict):
        """Validate contact information"""
        # Phone validation (Israeli format)
        landline = data.get('landlinePhone', '')
        mobile = data.get('mobilePhone', '')

        if landline:
            is_valid_landline = self._validate_israeli_phone(landline, is_mobile=False)
            self.validation_results.append({
                'field': 'landlinePhone',
                'value': landline,
                'valid': is_valid_landline,
                'message': 'Valid landline format' if is_valid_landline else 'Invalid landline format'
            })

        if mobile:
            is_valid_mobile = self._validate_israeli_phone(mobile, is_mobile=True)
            self.validation_results.append({
                'field': 'mobilePhone',
                'value': mobile,
                'valid': is_valid_mobile,
                'message': 'Valid mobile format' if is_valid_mobile else 'Invalid mobile format'
            })

        # Address validation
        address = data.get('address', {})
        if isinstance(address, dict):
            has_street = bool(address.get('street', '').strip())
            has_city = bool(address.get('city', '').strip())

            self.validation_results.append({
                'field': 'address',
                'value': f"{address.get('street', '')} {address.get('houseNumber', '')}, {address.get('city', '')}",
                'valid': has_street and has_city,
                'message': 'Address has street and city' if (
                        has_street and has_city) else 'Incomplete address information'
            })

    def _validate_accident_info(self, data: Dict):
        """Validate accident-related information"""
        # Check if accident description exists
        description = data.get('accidentDescription', '')
        self.validation_results.append({
            'field': 'accidentDescription',
            'value': description,
            'valid': len(description.strip()) > 10,
            'message': 'Adequate accident description' if len(
                description.strip()) > 10 else 'Missing or insufficient accident description'
        })

        # Check if injured body part is specified
        injured_part = data.get('injuredBodyPart', '')
        self.validation_results.append({
            'field': 'injuredBodyPart',
            'value': injured_part,
            'valid': len(injured_part.strip()) > 0,
            'message': 'Injured body part specified' if injured_part.strip() else 'Injured body part not specified'
        })

        # Check time of injury format
        time_of_injury = data.get('timeOfInjury', '')
        if time_of_injury:
            is_valid_time = self._validate_time_format(time_of_injury)
            self.validation_results.append({
                'field': 'timeOfInjury',
                'value': time_of_injury,
                'valid': is_valid_time,
                'message': 'Valid time format' if is_valid_time else 'Invalid time format'
            })

    def _validate_israeli_id(self, id_number: str) -> bool:
        """Validate Israeli ID number format and checksum"""
        # Remove any non-digit characters
        id_clean = re.sub(r'\D', '', id_number)

        # Must be exactly 9 digits
        if len(id_clean) != 9:
            print("Invalid ID length: must be 9 digits")
            return False

        # Validate checksum using Israeli ID algorithm
        # try:
        #     total = 0
        #     for i, digit in enumerate(id_clean):
        #         num = int(digit) * ((i % 2) + 1)
        #         total += num if num < 10 else (num // 10) + (num % 10)
        #
        #     return total % 10 == 0
        # except:
        #     return False

    def _validate_israeli_phone(self, phone: str, is_mobile: bool = True) -> bool:
        """Validate Israeli phone number format"""
        # Remove any non-digit characters except +
        phone_clean = re.sub(r'[^\d+]', '', phone)

        # Remove country code if present
        if phone_clean.startswith('+972'):
            phone_clean = phone_clean[4:]
        elif phone_clean.startswith('972'):
            phone_clean = phone_clean[3:]
        elif phone_clean.startswith('0'):
            phone_clean = phone_clean[1:]

        if is_mobile:
            # Israeli mobile: starts with 5 and has 8 more digits
            return len(phone_clean) == 9 and phone_clean.startswith('5')
        else:
            # Israeli landline: various area codes, 8-9 digits total
            return len(phone_clean) in [8, 9] and not phone_clean.startswith('5')

    def _validate_date_object(self, date_obj: Dict) -> Tuple[bool, str]:
        """Validate a date object with day, month, year"""
        day = date_obj.get('day', '')
        month = date_obj.get('month', '')
        year = date_obj.get('year', '')

        if not all([day, month, year]):
            return False, "Incomplete date information"

        try:
            day_int = int(day)
            month_int = int(month)
            year_int = int(year)

            # Basic range validation
            if not (1 <= day_int <= 31):
                return False, "Invalid day"
            if not (1 <= month_int <= 12):
                return False, "Invalid month"
            if not (1900 <= year_int <= datetime.now().year + 1):
                return False, "Invalid year"

            # Try to create a valid date
            datetime(year_int, month_int, day_int)
            return True, "Valid date"

        except (ValueError, TypeError):
            return False, "Invalid date format"

    def _validate_time_format(self, time_str: str) -> bool:
        """Validate time format (HH:MM or HH.MM)"""
        time_patterns = [
            r'^\d{1,2}:\d{2}$',  # HH:MM
            r'^\d{1,2}\.\d{2}$',  # HH.MM
            r'^\d{1,2}:\d{2}:\d{2}$',  # HH:MM:SS
        ]

        return any(re.match(pattern, time_str.strip()) for pattern in time_patterns)

    def _calculate_completeness(self, data: Dict) -> float:
        """Calculate completeness score based on filled fields"""
        total_fields = 0
        filled_fields = 0

        def count_fields(obj, is_required=True):
            nonlocal total_fields, filled_fields

            if isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, dict):
                        count_fields(value, is_required)
                    else:
                        total_fields += 1
                        if value and str(value).strip():
                            filled_fields += 1
            elif isinstance(obj, str):
                total_fields += 1
                if obj.strip():
                    filled_fields += 1

        count_fields(data)
        return (filled_fields / total_fields * 100) if total_fields > 0 else 0

    def _generate_summary(self) -> str:
        """Generate a summary of validation results"""
        issues = [result for result in self.validation_results if not result['valid']]

        if not issues:
            return "All validations passed successfully."

        summary = f"Found {len(issues)} validation issues:\n"
        for issue in issues[:5]:  # Show top 5 issues
            summary += f"- {issue['field']}: {issue['message']}\n"

        if len(issues) > 5:
            summary += f"... and {len(issues) - 5} more issues."

        return summary
