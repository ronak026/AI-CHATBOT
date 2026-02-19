# FILE: chat/nlp/code_formatter.py
# Enhanced formatter for chatbot responses with multiple styling options

class ResponseFormatter:
    """Main class to format chatbot responses in different styles"""
    
    def __init__(self):
        self.SEPARATOR = "=" * 60
        self.SUBSEPARATOR = "-" * 60
    
    def format_code_block(self, code: str, language: str = "python") -> str:
        """
        Format code in a clean code block with language highlighting
        
        Args:
            code: The code to format
            language: Programming language (python, javascript, etc.)
        
        Returns:
            Formatted code block
        """
        code = code.strip()
        
        # Remove existing markdown if present
        if code.startswith("```"):
            code = code.split("\n", 1)[1] if "\n" in code else code
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        
        # Create formatted output
        output = f"\n{'='*60}\n"
        output += f"📝 {language.upper()} CODE\n"
        output += "="*60 + "\n\n"
        output += code + "\n\n"
        output += "="*60 + "\n"
        
        return output
    
    def format_response_with_box(self, response: str, title: str = "RESPONSE") -> str:
        """
        Format regular text response in a nice box
        
        Args:
            response: The text response
            title: Title for the box
        
        Returns:
            Boxed response
        """
        response = response.strip()
        
        output = f"\n┌{'─'*58}┐\n"
        output += f"│ {title:<56} │\n"
        output += f"├{'─'*58}┤\n"
        
        # Split response into lines and wrap them
        lines = response.split('\n')
        for line in lines:
            if len(line) > 56:
                # Wrap long lines
                words = line.split(' ')
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 56:
                        current_line += word + " "
                    else:
                        output += f"│ {current_line:<56} │\n"
                        current_line = word + " "
                if current_line:
                    output += f"│ {current_line:<56} │\n"
            else:
                output += f"│ {line:<56} │\n"
        
        output += f"└{'─'*58}┘\n"
        
        return output
    
    def format_response_simple(self, response: str, title: str = "ANSWER") -> str:
        """
        Simple format with separators (lightweight, easy to read)
        
        Args:
            response: The text response
            title: Section title
        
        Returns:
            Simply formatted response
        """
        output = f"\n{self.SEPARATOR}\n"
        output += f"➤ {title}\n"
        output += f"{self.SEPARATOR}\n"
        output += response.strip() + "\n"
        output += f"{self.SEPARATOR}\n"
        
        return output
    
    def format_code_with_numbers(self, code: str, language: str = "python") -> str:
        """
        Format code with line numbers
        
        Args:
            code: The code to format
            language: Programming language
        
        Returns:
            Code with line numbers
        """
        code = code.strip()
        
        # Remove markdown fences if present
        if code.startswith("```"):
            code = code.split("\n", 1)[1] if "\n" in code else code
        if code.endswith("```"):
            code = code[:-3]
        
        code = code.strip()
        lines = code.split('\n')
        
        # Add line numbers
        output = f"\n{'='*60}\n"
        output += f"📝 {language.upper()} CODE\n"
        output += "="*60 + "\n\n"
        
        max_line_num = len(lines)
        line_width = len(str(max_line_num))
        
        for i, line in enumerate(lines, 1):
            line_num = str(i).rjust(line_width)
            output += f" {line_num}|{line}\n"
        
        output += "\n" + "="*60 + "\n"
        
        return output
    
    def format_multiple_sections(self, sections: dict) -> str:
        """
        Format response with multiple sections
        
        Args:
            sections: Dictionary with section_name: content pairs
        
        Returns:
            Formatted multi-section response
        """
        output = f"\n{self.SEPARATOR}\n"
        
        for i, (title, content) in enumerate(sections.items(), 1):
            output += f"⦿ {title}\n"
            output += f"{self.SUBSEPARATOR}\n"
            output += str(content).strip() + "\n\n"
        
        output += f"{self.SEPARATOR}\n"
        
        return output
    
    def format_error(self, error_message: str) -> str:
        """Format error messages"""
        output = f"\n{'!'*60}\n"
        output += f"⚠️  ERROR\n"
        output += f"{'!'*60}\n"
        output += error_message.strip() + "\n"
        output += f"{'!'*60}\n"
        
        return output
    
    def format_success(self, message: str) -> str:
        """Format success messages"""
        output = f"\n{'✓'*30}\n"
        output += f"✓ SUCCESS\n"
        output += f"{'✓'*30}\n"
        output += message.strip() + "\n"
        output += f"{'✓'*30}\n"
        
        return output
    
    def detect_response_type(self, text: str) -> str:
        """
        Auto-detect if response contains code or regular text
        
        Returns:
            'code' or 'text'
        """
        code_indicators = [
            "def ", "class ", "import ", "function ", "const ", "let ",
            "var ", "SELECT ", "INSERT ", "<?php", "<!DOCTYPE", "return ",
            "if __name__", "async ", "await ", "=>", "${", "})"
        ]
        
        return 'code' if any(indicator in text for indicator in code_indicators) else 'text'


# Utility functions for easy use
formatter = ResponseFormatter()

def format_code(code: str, language: str = "python", with_numbers: bool = False) -> str:
    """Quick function to format code"""
    if with_numbers:
        return formatter.format_code_with_numbers(code, language)
    return formatter.format_code_block(code, language)

def format_text(text: str, title: str = "RESPONSE", style: str = "simple") -> str:
    """Quick function to format text responses"""
    if style == "box":
        return formatter.format_response_with_box(text, title)
    return formatter.format_response_simple(text, title)

def format_sections(sections: dict) -> str:
    """Quick function to format multiple sections"""
    return formatter.format_multiple_sections(sections)

def format_error(error: str) -> str:
    """Quick function to format errors"""
    return formatter.format_error(error)

def format_success(message: str) -> str:
    """Quick function to format success messages"""
    return formatter.format_success(message)

def format_code_simple(code: str, language: str = "python") -> str:
    """
    Format code with line numbers for frontend display in a code box.
    Format: "# LANGUAGE CODE" followed by "1|code" on each line
    This format is recognized by the frontend JavaScript parser and displayed in a box.
    REMOVES EMPTY LINES to reduce whitespace in the display.
    
    Args:
        code: The code to format
        language: Programming language (python, java, javascript, etc.)
    
    Returns:
        Formatted code string with header and line numbers (no empty lines)
    """
    if not code:
        return code
    
    code = code.strip()
    
    # Remove markdown code fences if present
    if code.startswith("```"):
        code = code.split("\n", 1)[1] if "\n" in code else code
    if code.endswith("```"):
        code = code[:-3]
    
    code = code.strip()
    lines = code.split('\n')
    
    # REMOVE EMPTY LINES - this is the key change!
    # Only keep lines that have content
    content_lines = [line for line in lines if line.strip()]
    
    # Add line numbers to each content line
    formatted_lines = []
    for i, line in enumerate(content_lines, 1):
        formatted_lines.append(f"{i}|{line}")
    
    # Add header in format: # LANGUAGE CODE
    # This header is detected by frontend JavaScript and triggers code box display
    header = f"# {language.upper()} CODE"
    formatted = header + "\n" + "\n".join(formatted_lines)
    
    return formatted

def is_code_response(text: str) -> bool:
    """
    Check if response contains code (has code blocks or code indicators)
    
    Args:
        text: The text to check
    
    Returns:
        True if text appears to be code, False otherwise
    """
    code_indicators = [
        "def ", "class ", "import ", "function ", "const ", "let ",
        "var ", "SELECT ", "INSERT ", "<?php", "<!DOCTYPE", "return ",
        "if __name__", "async ", "await ", "=>", "${", "})", "function(",
        "<script>", "<style>", "console.log", "print(", "for ", "while ",
        "public class ", "public static", "private ", "void main"
    ]
    
    return any(indicator in text for indicator in code_indicators)