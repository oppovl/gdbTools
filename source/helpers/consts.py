commandsNamePrefix = ""

from enum import Enum

class StlContainer(Enum):
    ARRAY           = "std::array",
    LIST            = "std::list",
    VECTOR          = "std::vector",
    STACK           = "std::stack",
    DEQUE           = "std::deque",
    QUEUE           = "std::queue",
    PRIOR_QUEUE     = "std::priority_queue",
    MAP             = "std::map",
    UNORD_MAP       = "std::unordered_map",
    MULT_MAP        = "std::multimap",
    UNORD_MULT_MAP  = "std::unordered_multimap",
    SET             = "std::set",
    UNORD_SET       = "std::unordered_set",
    MULT_SET        = "std::multiset",
    UNORD_MULT_SET  = "std::unordered_multiset",
    UNKNOWN         = ""


typedef_stl_strings_map = {
    "std::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>": "std::string",
    "std::basic_string<char,std::char_traits<char>,std::allocator<char>>": "std::string",

    "std::__cxx11::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t>>": "std::wstring",
    "std::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t>>": "std::wstring",

    "std::__cxx11::basic_string<char8_t,std::char_traits<char8_t>,std::allocator<char8_t>>": "std::u8string",
    "std::basic_string<char8_t,std::char_traits<char8_t>,std::allocator<char8_t>>": "std::u8string",

    "std::__cxx11::basic_string<char16_t,std::char_traits<char16_t>,std::allocator<char16_t>>": "std::u16string",
    "std::basic_string<char16_t,std::char_traits<char16_t>,std::allocator<char16_t>>": "std::u16string",

    "std::__cxx11::basic_string<char32_t,std::char_traits<char32_t>,std::allocator<char32_t>>": "std::u32string",
    "std::basic_string<char32_t,std::char_traits<char32_t>,std::allocator<char32_t>>": "std::u32string",

    # const strings
    "conststd::__cxx11::basic_string<char,std::char_traits<char>,std::allocator<char>>": "const std::string",
    "conststd::basic_string<char,std::char_traits<char>,std::allocator<char>>": "const std::string",

    "conststd::__cxx11::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t>>": "const std::wstring",
    "conststd::basic_string<wchar_t,std::char_traits<wchar_t>,std::allocator<wchar_t>>": "const std::wstring",

    "conststd::__cxx11::basic_string<char8_t,std::char_traits<char8_t>,std::allocator<char8_t>>": "const std::u8string",
    "conststd::basic_string<char8_t,std::char_traits<char8_t>,std::allocator<char8_t>>": "const std::u8string",

    "conststd::__cxx11::basic_string<char16_t,std::char_traits<char16_t>,std::allocator<char16_t>>": "const std::u16string",
    "conststd::basic_string<char16_t,std::char_traits<char16_t>,std::allocator<char16_t>>": "const std::u16string",

    "conststd::__cxx11::basic_string<char32_t,std::char_traits<char32_t>,std::allocator<char32_t>>": "const std::u32string",
    "conststd::basic_string<char32_t,std::char_traits<char32_t>,std::allocator<char32_t>>": "const std::u32string"
}