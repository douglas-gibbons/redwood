import unittest
from  ..config import Config
import os

def test_config_loading_and_access():

    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, 'test_redwood.yaml')
    conf = Config(config_path)

    unittest.TestCase().assertEqual(conf.model.name, "gemini-2.5-flash")
    unittest.TestCase().assertEqual(conf.model.api_key, "TEST-API-KEY")
    unittest.TestCase().assertEqual(conf.max_model_calls, 20)
    unittest.TestCase().assertEqual(conf.prompt.strip(), "Test prompt content")
    
    with unittest.TestCase().assertRaises(AttributeError):
         _ = conf.munch.non_existent_attribute

    with unittest.TestCase().assertRaises(AttributeError):
         _ = conf.munch.model.non_existent_attribute

    unittest.TestCase().assertTrue(conf.exists("model"))
    unittest.TestCase().assertFalse(conf.exists("non_existent_section"))
    unittest.TestCase().assertTrue(conf.exists("model.name"))
    unittest.TestCase().assertFalse(conf.exists("model.non_existent_section"))
    