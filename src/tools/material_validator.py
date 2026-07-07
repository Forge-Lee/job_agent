import string

class MaterialValidator():
    def _count_words(self, text: str):
        text_splitted = text.split(' ')
        word_counter = 0
        for txt in text_splitted:
            if txt not in string.punctuation:
                word_counter += 1
        
        return word_counter

    def _find_placeholders(self, text):
        placeholder_list = [
            "[Company]",
            "[Date]",
            "[Hiring Manager]",
            "[Your Name]",
            "[Recruiter Name]",
            "[Project]",
            "[Metric]",
            "TODO",
            "XXX"
        ]

        for placeholder in placeholder_list:
            if placeholder in text:
                return True
        
        return False

    def _contains_company_or_role(self, text, parsed_jd):
        company = parsed_jd.company
        role = parsed_jd.role
        text_lower = text.lower()
        company_flag = False
        role_flag = False
        company_flag = company.lower() in text_lower
        role_flag = role.lower() in text_lower
        
        res = {
            'contain_company': company_flag,
            'contain_role': role_flag
        }
        return res

    def _find_high_risk_claims(self, text, candidate_profile):
        pass

    def validate_cover_letter(self, text, parsed_jd, candidate_profile):
        number_of_words = self._count_words(text)
        has_placeholder = self._find_placeholders(text)
        contains_comp_role = self._contains_company_or_role(text, parsed_jd)

        errors = []
        warnings = []
        if number_of_words == 0:
            errors.append('empty text')
        elif number_of_words < 120:
            errors.append('word count < 120')
        elif number_of_words > 450:
            warnings.append('word count > 450')
        
        if has_placeholder:
            warnings.append('contains placeholder')
        
        if not contains_comp_role['contain_company']:
            warnings.append('does not mention company')
        
        if not contains_comp_role['contain_role']:
            warnings.append('does not mention role')
        
        res = {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "word_count": number_of_words
        }

        return res

    def validate_linkedin_message(self, text, parsed_jd, candidate_profile):
        number_of_words = self._count_words(text)
        has_placeholder = self._find_placeholders(text)
        contains_comp_role = self._contains_company_or_role(text, parsed_jd)

        errors = []
        warnings = []
        if number_of_words == 0:
            errors.append('empty text')
        elif number_of_words < 30:
            errors.append('word count < 30')
        elif number_of_words > 150:
            warnings.append('word count > 150')
        
        if has_placeholder:
            warnings.append('contains placeholder')
        
        if not contains_comp_role['contain_company']:
            warnings.append('does not mention company')
        
        if not contains_comp_role['contain_role']:
            warnings.append('does not mention role')
        
        res = {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "word_count": number_of_words
        }

        return res

    def validate_resume_bullets(self, text, parsed_jd, candidate_profile):
        bullet_lines = [
            line for line in text.splitlines()
            if line.strip().startswith("-")
        ]

        has_placeholder = self._find_placeholders(text)

        errors = []
        warnings = []
        bullet_length = len(bullet_lines)
        if bullet_length > 7:
            warnings.append('more than 7 bullet lines')
        if bullet_length < 2:
            errors.append('fewer than 2 bullet lines')
        if not text.strip():
            errors.append("empty text")

        if has_placeholder:
            warnings.append('contains placeholder')

        first_person = ['i', 'my']
        contain_first_person = False
        for line in bullet_lines:
            line_splitted = line.split(' ')
            for chars in line_splitted:
                chars = chars.strip(string.punctuation).lower()
                if chars in first_person:
                    contain_first_person = True
                    break
            
            if contain_first_person:
                warnings.append('contains first-person language: "I ", "my "')
                break
        
        res = {
            "passed": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "bullets_count": bullet_length
        }

        return res