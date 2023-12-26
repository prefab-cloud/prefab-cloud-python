# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: prefab.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0cprefab.proto\x12\x06prefab\"{\n\x14\x43onfigServicePointer\x12\x1d\n\nproject_id\x18\x01 \x01(\x03R\tprojectId\x12\x1e\n\x0bstart_at_id\x18\x02 \x01(\x03R\tstartAtId\x12$\n\x0eproject_env_id\x18\x03 \x01(\x03R\x0cprojectEnvId\"\xd0\x04\n\x0b\x43onfigValue\x12\x12\n\x03int\x18\x01 \x01(\x03H\x00R\x03int\x12\x18\n\x06string\x18\x02 \x01(\tH\x00R\x06string\x12\x16\n\x05\x62ytes\x18\x03 \x01(\x0cH\x00R\x05\x62ytes\x12\x18\n\x06\x64ouble\x18\x04 \x01(\x01H\x00R\x06\x64ouble\x12\x14\n\x04\x62ool\x18\x05 \x01(\x08H\x00R\x04\x62ool\x12\x41\n\x0fweighted_values\x18\x06 \x01(\x0b\x32\x16.prefab.WeightedValuesH\x00R\x0eweightedValues\x12\x44\n\x10limit_definition\x18\x07 \x01(\x0b\x32\x17.prefab.LimitDefinitionH\x00R\x0flimitDefinition\x12/\n\tlog_level\x18\t \x01(\x0e\x32\x10.prefab.LogLevelH\x00R\x08logLevel\x12\x35\n\x0bstring_list\x18\n \x01(\x0b\x32\x12.prefab.StringListH\x00R\nstringList\x12/\n\tint_range\x18\x0b \x01(\x0b\x32\x10.prefab.IntRangeH\x00R\x08intRange\x12.\n\x08provided\x18\x0c \x01(\x0b\x32\x10.prefab.ProvidedH\x00R\x08provided\x12\'\n\x0c\x63onfidential\x18\r \x01(\x08H\x01R\x0c\x63onfidential\x88\x01\x01\x12&\n\x0c\x64\x65\x63rypt_with\x18\x0e \x01(\tH\x02R\x0b\x64\x65\x63ryptWith\x88\x01\x01\x42\x06\n\x04typeB\x0f\n\r_confidentialB\x0f\n\r_decrypt_with\"r\n\x08Provided\x12\x33\n\x06source\x18\x01 \x01(\x0e\x32\x16.prefab.ProvidedSourceH\x00R\x06source\x88\x01\x01\x12\x1b\n\x06lookup\x18\x02 \x01(\tH\x01R\x06lookup\x88\x01\x01\x42\t\n\x07_sourceB\t\n\x07_lookup\"N\n\x08IntRange\x12\x19\n\x05start\x18\x01 \x01(\x03H\x00R\x05start\x88\x01\x01\x12\x15\n\x03\x65nd\x18\x02 \x01(\x03H\x01R\x03\x65nd\x88\x01\x01\x42\x08\n\x06_startB\x06\n\x04_end\"$\n\nStringList\x12\x16\n\x06values\x18\x01 \x03(\tR\x06values\"R\n\rWeightedValue\x12\x16\n\x06weight\x18\x01 \x01(\x05R\x06weight\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x13.prefab.ConfigValueR\x05value\"\xa2\x01\n\x0eWeightedValues\x12>\n\x0fweighted_values\x18\x01 \x03(\x0b\x32\x15.prefab.WeightedValueR\x0eweightedValues\x12\x36\n\x15hash_by_property_name\x18\x02 \x01(\tH\x00R\x12hashByPropertyName\x88\x01\x01\x42\x18\n\x16_hash_by_property_name\"g\n\x0e\x41piKeyMetadata\x12\x1a\n\x06key_id\x18\x01 \x01(\tH\x00R\x05keyId\x88\x01\x01\x12\x1c\n\x07user_id\x18\x03 \x01(\tH\x01R\x06userId\x88\x01\x01\x42\t\n\x07_key_idB\n\n\x08_user_idJ\x04\x08\x02\x10\x03\"\xea\x02\n\x07\x43onfigs\x12(\n\x07\x63onfigs\x18\x01 \x03(\x0b\x32\x0e.prefab.ConfigR\x07\x63onfigs\x12R\n\x16\x63onfig_service_pointer\x18\x02 \x01(\x0b\x32\x1c.prefab.ConfigServicePointerR\x14\x63onfigServicePointer\x12\x44\n\x0f\x61pikey_metadata\x18\x03 \x01(\x0b\x32\x16.prefab.ApiKeyMetadataH\x00R\x0e\x61pikeyMetadata\x88\x01\x01\x12@\n\x0f\x64\x65\x66\x61ult_context\x18\x04 \x01(\x0b\x32\x12.prefab.ContextSetH\x01R\x0e\x64\x65\x66\x61ultContext\x88\x01\x01\x12\"\n\nkeep_alive\x18\x05 \x01(\x08H\x02R\tkeepAlive\x88\x01\x01\x42\x12\n\x10_apikey_metadataB\x12\n\x10_default_contextB\r\n\x0b_keep_alive\"\xcb\x04\n\x06\x43onfig\x12\x0e\n\x02id\x18\x01 \x01(\x03R\x02id\x12\x1d\n\nproject_id\x18\x02 \x01(\x03R\tprojectId\x12\x10\n\x03key\x18\x03 \x01(\tR\x03key\x12\x30\n\nchanged_by\x18\x04 \x01(\x0b\x32\x11.prefab.ChangedByR\tchangedBy\x12%\n\x04rows\x18\x05 \x03(\x0b\x32\x11.prefab.ConfigRowR\x04rows\x12>\n\x10\x61llowable_values\x18\x06 \x03(\x0b\x32\x13.prefab.ConfigValueR\x0f\x61llowableValues\x12\x33\n\x0b\x63onfig_type\x18\x07 \x01(\x0e\x32\x12.prefab.ConfigTypeR\nconfigType\x12\x1e\n\x08\x64raft_id\x18\x08 \x01(\x03H\x00R\x07\x64raftId\x88\x01\x01\x12\x37\n\nvalue_type\x18\t \x01(\x0e\x32\x18.prefab.Config.ValueTypeR\tvalueType\x12+\n\x12send_to_client_sdk\x18\n \x01(\x08R\x0fsendToClientSdk\"\x9e\x01\n\tValueType\x12\x16\n\x12NOT_SET_VALUE_TYPE\x10\x00\x12\x07\n\x03INT\x10\x01\x12\n\n\x06STRING\x10\x02\x12\t\n\x05\x42YTES\x10\x03\x12\n\n\x06\x44OUBLE\x10\x04\x12\x08\n\x04\x42OOL\x10\x05\x12\x14\n\x10LIMIT_DEFINITION\x10\x07\x12\r\n\tLOG_LEVEL\x10\t\x12\x0f\n\x0bSTRING_LIST\x10\n\x12\r\n\tINT_RANGE\x10\x0b\x42\x0b\n\t_draft_id\"X\n\tChangedBy\x12\x17\n\x07user_id\x18\x01 \x01(\x03R\x06userId\x12\x14\n\x05\x65mail\x18\x02 \x01(\tR\x05\x65mail\x12\x1c\n\napi_key_id\x18\x03 \x01(\tR\x08\x61piKeyId\"\x92\x02\n\tConfigRow\x12)\n\x0eproject_env_id\x18\x01 \x01(\x03H\x00R\x0cprojectEnvId\x88\x01\x01\x12\x30\n\x06values\x18\x02 \x03(\x0b\x32\x18.prefab.ConditionalValueR\x06values\x12\x41\n\nproperties\x18\x03 \x03(\x0b\x32!.prefab.ConfigRow.PropertiesEntryR\nproperties\x1aR\n\x0fPropertiesEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x13.prefab.ConfigValueR\x05value:\x02\x38\x01\x42\x11\n\x0f_project_env_id\"l\n\x10\x43onditionalValue\x12-\n\x08\x63riteria\x18\x01 \x03(\x0b\x32\x11.prefab.CriterionR\x08\x63riteria\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x13.prefab.ConfigValueR\x05value\"\xba\x03\n\tCriterion\x12#\n\rproperty_name\x18\x01 \x01(\tR\x0cpropertyName\x12?\n\x08operator\x18\x02 \x01(\x0e\x32#.prefab.Criterion.CriterionOperatorR\x08operator\x12\x39\n\x0evalue_to_match\x18\x03 \x01(\x0b\x32\x13.prefab.ConfigValueR\x0cvalueToMatch\"\x8b\x02\n\x11\x43riterionOperator\x12\x0b\n\x07NOT_SET\x10\x00\x12\x11\n\rLOOKUP_KEY_IN\x10\x01\x12\x15\n\x11LOOKUP_KEY_NOT_IN\x10\x02\x12\n\n\x06IN_SEG\x10\x03\x12\x0e\n\nNOT_IN_SEG\x10\x04\x12\x0f\n\x0b\x41LWAYS_TRUE\x10\x05\x12\x12\n\x0ePROP_IS_ONE_OF\x10\x06\x12\x16\n\x12PROP_IS_NOT_ONE_OF\x10\x07\x12\x19\n\x15PROP_ENDS_WITH_ONE_OF\x10\x08\x12!\n\x1dPROP_DOES_NOT_END_WITH_ONE_OF\x10\t\x12\x16\n\x12HIERARCHICAL_MATCH\x10\n\x12\x10\n\x0cIN_INT_RANGE\x10\x0b\"\xbb\x01\n\x07Loggers\x12(\n\x07loggers\x18\x01 \x03(\x0b\x32\x0e.prefab.LoggerR\x07loggers\x12\x19\n\x08start_at\x18\x02 \x01(\x03R\x07startAt\x12\x15\n\x06\x65nd_at\x18\x03 \x01(\x03R\x05\x65ndAt\x12#\n\rinstance_hash\x18\x04 \x01(\tR\x0cinstanceHash\x12!\n\tnamespace\x18\x05 \x01(\tH\x00R\tnamespace\x88\x01\x01\x42\x0c\n\n_namespace\"\x93\x02\n\x06Logger\x12\x1f\n\x0blogger_name\x18\x01 \x01(\tR\nloggerName\x12\x1b\n\x06traces\x18\x02 \x01(\x03H\x00R\x06traces\x88\x01\x01\x12\x1b\n\x06\x64\x65\x62ugs\x18\x03 \x01(\x03H\x01R\x06\x64\x65\x62ugs\x88\x01\x01\x12\x19\n\x05infos\x18\x04 \x01(\x03H\x02R\x05infos\x88\x01\x01\x12\x19\n\x05warns\x18\x05 \x01(\x03H\x03R\x05warns\x88\x01\x01\x12\x1b\n\x06\x65rrors\x18\x06 \x01(\x03H\x04R\x06\x65rrors\x88\x01\x01\x12\x1b\n\x06\x66\x61tals\x18\x07 \x01(\x03H\x05R\x06\x66\x61tals\x88\x01\x01\x42\t\n\x07_tracesB\t\n\x07_debugsB\x08\n\x06_infosB\x08\n\x06_warnsB\t\n\x07_errorsB\t\n\x07_fatals\"\x16\n\x14LoggerReportResponse\"\xd5\x04\n\rLimitResponse\x12\x16\n\x06passed\x18\x01 \x01(\x08R\x06passed\x12\x1d\n\nexpires_at\x18\x02 \x01(\x03R\texpiresAt\x12%\n\x0e\x65nforced_group\x18\x03 \x01(\tR\renforcedGroup\x12%\n\x0e\x63urrent_bucket\x18\x04 \x01(\x03R\rcurrentBucket\x12!\n\x0cpolicy_group\x18\x05 \x01(\tR\x0bpolicyGroup\x12G\n\x0bpolicy_name\x18\x06 \x01(\x0e\x32&.prefab.LimitResponse.LimitPolicyNamesR\npolicyName\x12!\n\x0cpolicy_limit\x18\x07 \x01(\x05R\x0bpolicyLimit\x12\x16\n\x06\x61mount\x18\x08 \x01(\x03R\x06\x61mount\x12$\n\x0elimit_reset_at\x18\t \x01(\x03R\x0climitResetAt\x12\x46\n\x0csafety_level\x18\n \x01(\x0e\x32#.prefab.LimitDefinition.SafetyLevelR\x0bsafetyLevel\"\xa9\x01\n\x10LimitPolicyNames\x12\x0b\n\x07NOT_SET\x10\x00\x12\x14\n\x10SECONDLY_ROLLING\x10\x01\x12\x14\n\x10MINUTELY_ROLLING\x10\x03\x12\x12\n\x0eHOURLY_ROLLING\x10\x05\x12\x11\n\rDAILY_ROLLING\x10\x07\x12\x13\n\x0fMONTHLY_ROLLING\x10\x08\x12\x0c\n\x08INFINITE\x10\t\x12\x12\n\x0eYEARLY_ROLLING\x10\n\"\xed\x02\n\x0cLimitRequest\x12\x1d\n\naccount_id\x18\x01 \x01(\x03R\taccountId\x12%\n\x0e\x61\x63quire_amount\x18\x02 \x01(\x05R\racquireAmount\x12\x16\n\x06groups\x18\x03 \x03(\tR\x06groups\x12I\n\x0elimit_combiner\x18\x04 \x01(\x0e\x32\".prefab.LimitRequest.LimitCombinerR\rlimitCombiner\x12\x34\n\x16\x61llow_partial_response\x18\x05 \x01(\x08R\x14\x61llowPartialResponse\x12\x46\n\x0csafety_level\x18\x06 \x01(\x0e\x32#.prefab.LimitDefinition.SafetyLevelR\x0bsafetyLevel\"6\n\rLimitCombiner\x12\x0b\n\x07NOT_SET\x10\x00\x12\x0b\n\x07MINIMUM\x10\x01\x12\x0b\n\x07MAXIMUM\x10\x02\"9\n\nContextSet\x12+\n\x08\x63ontexts\x18\x01 \x03(\x0b\x32\x0f.prefab.ContextR\x08\x63ontexts\"\xb0\x01\n\x07\x43ontext\x12\x17\n\x04type\x18\x01 \x01(\tH\x00R\x04type\x88\x01\x01\x12\x33\n\x06values\x18\x02 \x03(\x0b\x32\x1b.prefab.Context.ValuesEntryR\x06values\x1aN\n\x0bValuesEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12)\n\x05value\x18\x02 \x01(\x0b\x32\x13.prefab.ConfigValueR\x05value:\x02\x38\x01\x42\x07\n\x05_type\"\xb3\x01\n\x08Identity\x12\x1b\n\x06lookup\x18\x01 \x01(\tH\x00R\x06lookup\x88\x01\x01\x12@\n\nattributes\x18\x02 \x03(\x0b\x32 .prefab.Identity.AttributesEntryR\nattributes\x1a=\n\x0f\x41ttributesEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value:\x02\x38\x01\x42\t\n\x07_lookup\"\xa6\x03\n\x18\x43onfigEvaluationMetaData\x12-\n\x10\x63onfig_row_index\x18\x01 \x01(\x03H\x00R\x0e\x63onfigRowIndex\x88\x01\x01\x12;\n\x17\x63onditional_value_index\x18\x02 \x01(\x03H\x01R\x15\x63onditionalValueIndex\x88\x01\x01\x12\x35\n\x14weighted_value_index\x18\x03 \x01(\x03H\x02R\x12weightedValueIndex\x88\x01\x01\x12+\n\x04type\x18\x04 \x01(\x0e\x32\x12.prefab.ConfigTypeH\x03R\x04type\x88\x01\x01\x12\x13\n\x02id\x18\x05 \x01(\x03H\x04R\x02id\x88\x01\x01\x12<\n\nvalue_type\x18\x06 \x01(\x0e\x32\x18.prefab.Config.ValueTypeH\x05R\tvalueType\x88\x01\x01\x42\x13\n\x11_config_row_indexB\x1a\n\x18_conditional_value_indexB\x17\n\x15_weighted_value_indexB\x07\n\x05_typeB\x05\n\x03_idB\r\n\x0b_value_type\"\x96\x03\n\x11\x43lientConfigValue\x12\x12\n\x03int\x18\x01 \x01(\x03H\x00R\x03int\x12\x18\n\x06string\x18\x02 \x01(\tH\x00R\x06string\x12\x18\n\x06\x64ouble\x18\x03 \x01(\x01H\x00R\x06\x64ouble\x12\x14\n\x04\x62ool\x18\x04 \x01(\x08H\x00R\x04\x62ool\x12/\n\tlog_level\x18\x05 \x01(\x0e\x32\x10.prefab.LogLevelH\x00R\x08logLevel\x12\x35\n\x0bstring_list\x18\x07 \x01(\x0b\x32\x12.prefab.StringListH\x00R\nstringList\x12/\n\tint_range\x18\x08 \x01(\x0b\x32\x10.prefab.IntRangeH\x00R\x08intRange\x12\x63\n\x1a\x63onfig_evaluation_metadata\x18\x06 \x01(\x0b\x32 .prefab.ConfigEvaluationMetaDataH\x01R\x18\x63onfigEvaluationMetadata\x88\x01\x01\x42\x06\n\x04typeB\x1d\n\x1b_config_evaluation_metadata\"\xd8\x02\n\x11\x43onfigEvaluations\x12=\n\x06values\x18\x01 \x03(\x0b\x32%.prefab.ConfigEvaluations.ValuesEntryR\x06values\x12\x44\n\x0f\x61pikey_metadata\x18\x02 \x01(\x0b\x32\x16.prefab.ApiKeyMetadataH\x00R\x0e\x61pikeyMetadata\x88\x01\x01\x12@\n\x0f\x64\x65\x66\x61ult_context\x18\x03 \x01(\x0b\x32\x12.prefab.ContextSetH\x01R\x0e\x64\x65\x66\x61ultContext\x88\x01\x01\x1aT\n\x0bValuesEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12/\n\x05value\x18\x02 \x01(\x0b\x32\x19.prefab.ClientConfigValueR\x05value:\x02\x38\x01\x42\x12\n\x10_apikey_metadataB\x12\n\x10_default_context\"\xf4\x02\n\x0fLimitDefinition\x12G\n\x0bpolicy_name\x18\x02 \x01(\x0e\x32&.prefab.LimitResponse.LimitPolicyNamesR\npolicyName\x12\x14\n\x05limit\x18\x03 \x01(\x05R\x05limit\x12\x14\n\x05\x62urst\x18\x04 \x01(\x05R\x05\x62urst\x12\x1d\n\naccount_id\x18\x05 \x01(\x03R\taccountId\x12#\n\rlast_modified\x18\x06 \x01(\x03R\x0clastModified\x12\x1e\n\nreturnable\x18\x07 \x01(\x08R\nreturnable\x12\x46\n\x0csafety_level\x18\x08 \x01(\x0e\x32#.prefab.LimitDefinition.SafetyLevelR\x0bsafetyLevel\"@\n\x0bSafetyLevel\x12\x0b\n\x07NOT_SET\x10\x00\x12\x12\n\x0eL4_BEST_EFFORT\x10\x04\x12\x10\n\x0cL5_BOMBPROOF\x10\x05\"M\n\x10LimitDefinitions\x12\x39\n\x0b\x64\x65\x66initions\x18\x01 \x03(\x0b\x32\x17.prefab.LimitDefinitionR\x0b\x64\x65\x66initions\"\xc8\x01\n\x0f\x42ufferedRequest\x12\x1d\n\naccount_id\x18\x01 \x01(\x03R\taccountId\x12\x16\n\x06method\x18\x02 \x01(\tR\x06method\x12\x10\n\x03uri\x18\x03 \x01(\tR\x03uri\x12\x12\n\x04\x62ody\x18\x04 \x01(\tR\x04\x62ody\x12!\n\x0climit_groups\x18\x05 \x03(\tR\x0blimitGroups\x12!\n\x0c\x63ontent_type\x18\x06 \x01(\tR\x0b\x63ontentType\x12\x12\n\x04\x66ifo\x18\x07 \x01(\x08R\x04\x66ifo\"\xde\x01\n\x0c\x42\x61tchRequest\x12\x1d\n\naccount_id\x18\x01 \x01(\x03R\taccountId\x12\x16\n\x06method\x18\x02 \x01(\tR\x06method\x12\x10\n\x03uri\x18\x03 \x01(\tR\x03uri\x12\x12\n\x04\x62ody\x18\x04 \x01(\tR\x04\x62ody\x12!\n\x0climit_groups\x18\x05 \x03(\tR\x0blimitGroups\x12%\n\x0e\x62\x61tch_template\x18\x06 \x01(\tR\rbatchTemplate\x12\'\n\x0f\x62\x61tch_separator\x18\x07 \x01(\tR\x0e\x62\x61tchSeparator\")\n\rBasicResponse\x12\x18\n\x07message\x18\x01 \x01(\tR\x07message\"C\n\x10\x43reationResponse\x12\x18\n\x07message\x18\x01 \x01(\tR\x07message\x12\x15\n\x06new_id\x18\x02 \x01(\x03R\x05newId\"\x9b\x01\n\x07IdBlock\x12\x1d\n\nproject_id\x18\x01 \x01(\x03R\tprojectId\x12$\n\x0eproject_env_id\x18\x02 \x01(\x03R\x0cprojectEnvId\x12#\n\rsequence_name\x18\x03 \x01(\tR\x0csequenceName\x12\x14\n\x05start\x18\x04 \x01(\x03R\x05start\x12\x10\n\x03\x65nd\x18\x05 \x01(\x03R\x03\x65nd\"\x8e\x01\n\x0eIdBlockRequest\x12\x1d\n\nproject_id\x18\x01 \x01(\x03R\tprojectId\x12$\n\x0eproject_env_id\x18\x02 \x01(\x03R\x0cprojectEnvId\x12#\n\rsequence_name\x18\x03 \x01(\tR\x0csequenceName\x12\x12\n\x04size\x18\x04 \x01(\x03R\x04size\"\xa8\x01\n\x0c\x43ontextShape\x12\x12\n\x04name\x18\x01 \x01(\tR\x04name\x12\x45\n\x0b\x66ield_types\x18\x02 \x03(\x0b\x32$.prefab.ContextShape.FieldTypesEntryR\nfieldTypes\x1a=\n\x0f\x46ieldTypesEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\x05R\x05value:\x02\x38\x01\"n\n\rContextShapes\x12,\n\x06shapes\x18\x01 \x03(\x0b\x32\x14.prefab.ContextShapeR\x06shapes\x12!\n\tnamespace\x18\x02 \x01(\tH\x00R\tnamespace\x88\x01\x01\x42\x0c\n\n_namespace\"T\n\rEvaluatedKeys\x12\x12\n\x04keys\x18\x01 \x03(\tR\x04keys\x12!\n\tnamespace\x18\x02 \x01(\tH\x00R\tnamespace\x88\x01\x01\x42\x0c\n\n_namespace\"\xc3\x01\n\x0f\x45valuatedConfig\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12%\n\x0e\x63onfig_version\x18\x02 \x01(\x03R\rconfigVersion\x12+\n\x06result\x18\x03 \x01(\x0b\x32\x13.prefab.ConfigValueR\x06result\x12,\n\x07\x63ontext\x18\x04 \x01(\x0b\x32\x12.prefab.ContextSetR\x07\x63ontext\x12\x1c\n\ttimestamp\x18\x05 \x01(\x03R\ttimestamp\"E\n\x10\x45valuatedConfigs\x12\x31\n\x07\x63onfigs\x18\x01 \x03(\x0b\x32\x17.prefab.EvaluatedConfigR\x07\x63onfigs\"\xb6\x04\n\x17\x43onfigEvaluationCounter\x12\x14\n\x05\x63ount\x18\x01 \x01(\x03R\x05\x63ount\x12 \n\tconfig_id\x18\x02 \x01(\x03H\x00R\x08\x63onfigId\x88\x01\x01\x12*\n\x0eselected_index\x18\x03 \x01(\rH\x01R\rselectedIndex\x88\x01\x01\x12?\n\x0eselected_value\x18\x04 \x01(\x0b\x32\x13.prefab.ConfigValueH\x02R\rselectedValue\x88\x01\x01\x12-\n\x10\x63onfig_row_index\x18\x05 \x01(\rH\x03R\x0e\x63onfigRowIndex\x88\x01\x01\x12;\n\x17\x63onditional_value_index\x18\x06 \x01(\rH\x04R\x15\x63onditionalValueIndex\x88\x01\x01\x12\x35\n\x14weighted_value_index\x18\x07 \x01(\rH\x05R\x12weightedValueIndex\x88\x01\x01\x12>\n\x06reason\x18\x08 \x01(\x0e\x32&.prefab.ConfigEvaluationCounter.ReasonR\x06reason\"\x15\n\x06Reason\x12\x0b\n\x07UNKNOWN\x10\x00\x42\x0c\n\n_config_idB\x11\n\x0f_selected_indexB\x11\n\x0f_selected_valueB\x13\n\x11_config_row_indexB\x1a\n\x18_conditional_value_indexB\x17\n\x15_weighted_value_index\"\x90\x01\n\x17\x43onfigEvaluationSummary\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12&\n\x04type\x18\x02 \x01(\x0e\x32\x12.prefab.ConfigTypeR\x04type\x12;\n\x08\x63ounters\x18\x03 \x03(\x0b\x32\x1f.prefab.ConfigEvaluationCounterR\x08\x63ounters\"\x82\x01\n\x19\x43onfigEvaluationSummaries\x12\x14\n\x05start\x18\x01 \x01(\x03R\x05start\x12\x10\n\x03\x65nd\x18\x02 \x01(\x03R\x03\x65nd\x12=\n\tsummaries\x18\x03 \x03(\x0b\x32\x1f.prefab.ConfigEvaluationSummaryR\tsummaries\"s\n\x15LoggersTelemetryEvent\x12(\n\x07loggers\x18\x01 \x03(\x0b\x32\x0e.prefab.LoggerR\x07loggers\x12\x19\n\x08start_at\x18\x02 \x01(\x03R\x07startAt\x12\x15\n\x06\x65nd_at\x18\x03 \x01(\x03R\x05\x65ndAt\"\xd9\x02\n\x0eTelemetryEvent\x12\x41\n\tsummaries\x18\x02 \x01(\x0b\x32!.prefab.ConfigEvaluationSummariesH\x00R\tsummaries\x12\x44\n\x10\x65xample_contexts\x18\x03 \x01(\x0b\x32\x17.prefab.ExampleContextsH\x00R\x0f\x65xampleContexts\x12\x38\n\x0c\x63lient_stats\x18\x04 \x01(\x0b\x32\x13.prefab.ClientStatsH\x00R\x0b\x63lientStats\x12\x39\n\x07loggers\x18\x05 \x01(\x0b\x32\x1d.prefab.LoggersTelemetryEventH\x00R\x07loggers\x12>\n\x0e\x63ontext_shapes\x18\x06 \x01(\x0b\x32\x15.prefab.ContextShapesH\x00R\rcontextShapesB\t\n\x07payload\"f\n\x0fTelemetryEvents\x12#\n\rinstance_hash\x18\x01 \x01(\tR\x0cinstanceHash\x12.\n\x06\x65vents\x18\x02 \x03(\x0b\x32\x16.prefab.TelemetryEventR\x06\x65vents\"3\n\x17TelemetryEventsResponse\x12\x18\n\x07success\x18\x01 \x01(\x08R\x07success\"E\n\x0f\x45xampleContexts\x12\x32\n\x08\x65xamples\x18\x01 \x03(\x0b\x32\x16.prefab.ExampleContextR\x08\x65xamples\"b\n\x0e\x45xampleContext\x12\x1c\n\ttimestamp\x18\x01 \x01(\x03R\ttimestamp\x12\x32\n\ncontextSet\x18\x02 \x01(\x0b\x32\x12.prefab.ContextSetR\ncontextSet\"e\n\x0b\x43lientStats\x12\x14\n\x05start\x18\x01 \x01(\x03R\x05start\x12\x10\n\x03\x65nd\x18\x02 \x01(\x03R\x03\x65nd\x12.\n\x13\x64ropped_event_count\x18\x03 \x01(\x04R\x11\x64roppedEventCount*:\n\x0eProvidedSource\x12\x1b\n\x17PROVIDED_SOURCE_NOT_SET\x10\x00\x12\x0b\n\x07\x45NV_VAR\x10\x01*\x82\x01\n\nConfigType\x12\x17\n\x13NOT_SET_CONFIG_TYPE\x10\x00\x12\n\n\x06\x43ONFIG\x10\x01\x12\x10\n\x0c\x46\x45\x41TURE_FLAG\x10\x02\x12\r\n\tLOG_LEVEL\x10\x03\x12\x0b\n\x07SEGMENT\x10\x04\x12\x14\n\x10LIMIT_DEFINITION\x10\x05\x12\x0b\n\x07\x44\x45LETED\x10\x06*a\n\x08LogLevel\x12\x15\n\x11NOT_SET_LOG_LEVEL\x10\x00\x12\t\n\x05TRACE\x10\x01\x12\t\n\x05\x44\x45\x42UG\x10\x02\x12\x08\n\x04INFO\x10\x03\x12\x08\n\x04WARN\x10\x05\x12\t\n\x05\x45RROR\x10\x06\x12\t\n\x05\x46\x41TAL\x10\t*G\n\tOnFailure\x12\x0b\n\x07NOT_SET\x10\x00\x12\x10\n\x0cLOG_AND_PASS\x10\x01\x12\x10\n\x0cLOG_AND_FAIL\x10\x02\x12\t\n\x05THROW\x10\x03\x42\x1d\n\x13\x63loud.prefab.domainB\x06Prefabb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'prefab_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\023cloud.prefab.domainB\006Prefab'
  _CONFIGROW_PROPERTIESENTRY._options = None
  _CONFIGROW_PROPERTIESENTRY._serialized_options = b'8\001'
  _CONTEXT_VALUESENTRY._options = None
  _CONTEXT_VALUESENTRY._serialized_options = b'8\001'
  _IDENTITY_ATTRIBUTESENTRY._options = None
  _IDENTITY_ATTRIBUTESENTRY._serialized_options = b'8\001'
  _CONFIGEVALUATIONS_VALUESENTRY._options = None
  _CONFIGEVALUATIONS_VALUESENTRY._serialized_options = b'8\001'
  _CONTEXTSHAPE_FIELDTYPESENTRY._options = None
  _CONTEXTSHAPE_FIELDTYPESENTRY._serialized_options = b'8\001'
  _globals['_PROVIDEDSOURCE']._serialized_start=9950
  _globals['_PROVIDEDSOURCE']._serialized_end=10008
  _globals['_CONFIGTYPE']._serialized_start=10011
  _globals['_CONFIGTYPE']._serialized_end=10141
  _globals['_LOGLEVEL']._serialized_start=10143
  _globals['_LOGLEVEL']._serialized_end=10240
  _globals['_ONFAILURE']._serialized_start=10242
  _globals['_ONFAILURE']._serialized_end=10313
  _globals['_CONFIGSERVICEPOINTER']._serialized_start=24
  _globals['_CONFIGSERVICEPOINTER']._serialized_end=147
  _globals['_CONFIGVALUE']._serialized_start=150
  _globals['_CONFIGVALUE']._serialized_end=742
  _globals['_PROVIDED']._serialized_start=744
  _globals['_PROVIDED']._serialized_end=858
  _globals['_INTRANGE']._serialized_start=860
  _globals['_INTRANGE']._serialized_end=938
  _globals['_STRINGLIST']._serialized_start=940
  _globals['_STRINGLIST']._serialized_end=976
  _globals['_WEIGHTEDVALUE']._serialized_start=978
  _globals['_WEIGHTEDVALUE']._serialized_end=1060
  _globals['_WEIGHTEDVALUES']._serialized_start=1063
  _globals['_WEIGHTEDVALUES']._serialized_end=1225
  _globals['_APIKEYMETADATA']._serialized_start=1227
  _globals['_APIKEYMETADATA']._serialized_end=1330
  _globals['_CONFIGS']._serialized_start=1333
  _globals['_CONFIGS']._serialized_end=1695
  _globals['_CONFIG']._serialized_start=1698
  _globals['_CONFIG']._serialized_end=2285
  _globals['_CONFIG_VALUETYPE']._serialized_start=2114
  _globals['_CONFIG_VALUETYPE']._serialized_end=2272
  _globals['_CHANGEDBY']._serialized_start=2287
  _globals['_CHANGEDBY']._serialized_end=2375
  _globals['_CONFIGROW']._serialized_start=2378
  _globals['_CONFIGROW']._serialized_end=2652
  _globals['_CONFIGROW_PROPERTIESENTRY']._serialized_start=2551
  _globals['_CONFIGROW_PROPERTIESENTRY']._serialized_end=2633
  _globals['_CONDITIONALVALUE']._serialized_start=2654
  _globals['_CONDITIONALVALUE']._serialized_end=2762
  _globals['_CRITERION']._serialized_start=2765
  _globals['_CRITERION']._serialized_end=3207
  _globals['_CRITERION_CRITERIONOPERATOR']._serialized_start=2940
  _globals['_CRITERION_CRITERIONOPERATOR']._serialized_end=3207
  _globals['_LOGGERS']._serialized_start=3210
  _globals['_LOGGERS']._serialized_end=3397
  _globals['_LOGGER']._serialized_start=3400
  _globals['_LOGGER']._serialized_end=3675
  _globals['_LOGGERREPORTRESPONSE']._serialized_start=3677
  _globals['_LOGGERREPORTRESPONSE']._serialized_end=3699
  _globals['_LIMITRESPONSE']._serialized_start=3702
  _globals['_LIMITRESPONSE']._serialized_end=4299
  _globals['_LIMITRESPONSE_LIMITPOLICYNAMES']._serialized_start=4130
  _globals['_LIMITRESPONSE_LIMITPOLICYNAMES']._serialized_end=4299
  _globals['_LIMITREQUEST']._serialized_start=4302
  _globals['_LIMITREQUEST']._serialized_end=4667
  _globals['_LIMITREQUEST_LIMITCOMBINER']._serialized_start=4613
  _globals['_LIMITREQUEST_LIMITCOMBINER']._serialized_end=4667
  _globals['_CONTEXTSET']._serialized_start=4669
  _globals['_CONTEXTSET']._serialized_end=4726
  _globals['_CONTEXT']._serialized_start=4729
  _globals['_CONTEXT']._serialized_end=4905
  _globals['_CONTEXT_VALUESENTRY']._serialized_start=4818
  _globals['_CONTEXT_VALUESENTRY']._serialized_end=4896
  _globals['_IDENTITY']._serialized_start=4908
  _globals['_IDENTITY']._serialized_end=5087
  _globals['_IDENTITY_ATTRIBUTESENTRY']._serialized_start=5015
  _globals['_IDENTITY_ATTRIBUTESENTRY']._serialized_end=5076
  _globals['_CONFIGEVALUATIONMETADATA']._serialized_start=5090
  _globals['_CONFIGEVALUATIONMETADATA']._serialized_end=5512
  _globals['_CLIENTCONFIGVALUE']._serialized_start=5515
  _globals['_CLIENTCONFIGVALUE']._serialized_end=5921
  _globals['_CONFIGEVALUATIONS']._serialized_start=5924
  _globals['_CONFIGEVALUATIONS']._serialized_end=6268
  _globals['_CONFIGEVALUATIONS_VALUESENTRY']._serialized_start=6144
  _globals['_CONFIGEVALUATIONS_VALUESENTRY']._serialized_end=6228
  _globals['_LIMITDEFINITION']._serialized_start=6271
  _globals['_LIMITDEFINITION']._serialized_end=6643
  _globals['_LIMITDEFINITION_SAFETYLEVEL']._serialized_start=6579
  _globals['_LIMITDEFINITION_SAFETYLEVEL']._serialized_end=6643
  _globals['_LIMITDEFINITIONS']._serialized_start=6645
  _globals['_LIMITDEFINITIONS']._serialized_end=6722
  _globals['_BUFFEREDREQUEST']._serialized_start=6725
  _globals['_BUFFEREDREQUEST']._serialized_end=6925
  _globals['_BATCHREQUEST']._serialized_start=6928
  _globals['_BATCHREQUEST']._serialized_end=7150
  _globals['_BASICRESPONSE']._serialized_start=7152
  _globals['_BASICRESPONSE']._serialized_end=7193
  _globals['_CREATIONRESPONSE']._serialized_start=7195
  _globals['_CREATIONRESPONSE']._serialized_end=7262
  _globals['_IDBLOCK']._serialized_start=7265
  _globals['_IDBLOCK']._serialized_end=7420
  _globals['_IDBLOCKREQUEST']._serialized_start=7423
  _globals['_IDBLOCKREQUEST']._serialized_end=7565
  _globals['_CONTEXTSHAPE']._serialized_start=7568
  _globals['_CONTEXTSHAPE']._serialized_end=7736
  _globals['_CONTEXTSHAPE_FIELDTYPESENTRY']._serialized_start=7675
  _globals['_CONTEXTSHAPE_FIELDTYPESENTRY']._serialized_end=7736
  _globals['_CONTEXTSHAPES']._serialized_start=7738
  _globals['_CONTEXTSHAPES']._serialized_end=7848
  _globals['_EVALUATEDKEYS']._serialized_start=7850
  _globals['_EVALUATEDKEYS']._serialized_end=7934
  _globals['_EVALUATEDCONFIG']._serialized_start=7937
  _globals['_EVALUATEDCONFIG']._serialized_end=8132
  _globals['_EVALUATEDCONFIGS']._serialized_start=8134
  _globals['_EVALUATEDCONFIGS']._serialized_end=8203
  _globals['_CONFIGEVALUATIONCOUNTER']._serialized_start=8206
  _globals['_CONFIGEVALUATIONCOUNTER']._serialized_end=8772
  _globals['_CONFIGEVALUATIONCOUNTER_REASON']._serialized_start=8625
  _globals['_CONFIGEVALUATIONCOUNTER_REASON']._serialized_end=8646
  _globals['_CONFIGEVALUATIONSUMMARY']._serialized_start=8775
  _globals['_CONFIGEVALUATIONSUMMARY']._serialized_end=8919
  _globals['_CONFIGEVALUATIONSUMMARIES']._serialized_start=8922
  _globals['_CONFIGEVALUATIONSUMMARIES']._serialized_end=9052
  _globals['_LOGGERSTELEMETRYEVENT']._serialized_start=9054
  _globals['_LOGGERSTELEMETRYEVENT']._serialized_end=9169
  _globals['_TELEMETRYEVENT']._serialized_start=9172
  _globals['_TELEMETRYEVENT']._serialized_end=9517
  _globals['_TELEMETRYEVENTS']._serialized_start=9519
  _globals['_TELEMETRYEVENTS']._serialized_end=9621
  _globals['_TELEMETRYEVENTSRESPONSE']._serialized_start=9623
  _globals['_TELEMETRYEVENTSRESPONSE']._serialized_end=9674
  _globals['_EXAMPLECONTEXTS']._serialized_start=9676
  _globals['_EXAMPLECONTEXTS']._serialized_end=9745
  _globals['_EXAMPLECONTEXT']._serialized_start=9747
  _globals['_EXAMPLECONTEXT']._serialized_end=9845
  _globals['_CLIENTSTATS']._serialized_start=9847
  _globals['_CLIENTSTATS']._serialized_end=9948
# @@protoc_insertion_point(module_scope)
