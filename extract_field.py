# 提取各个需要添加的字段graphql定义



data_type = {}
String_type = {}
Keyword_type = {}
Num_type = {}
String_first_type = {}
Num_first_type = {}
INDEX_fields = {}


# 预处理mappings，去除"properties"等不需要的信息，将每个字段分成几类，返回字段字典
def format_mappings(prefix, mappings):
	temp = {}
	mappings = mappings['properties']
	for data in mappings.items():
		if 'type' in data[1].keys():
			if data[1]['type'] == 'float' or data[1]['type'] == 'integer' or data[1]['type'] == 'ip':
				if data[1]['type'] == 'float':
					data[1]['type'] = "Float"
				elif data[1]['type'] == 'integer':
					data[1]['type'] = "Int"
				else:
					data[1]['type'] = "String"
				Num_type[prefix + data[0]] = data[1]['type']
				if prefix == '':
					Num_first_type[prefix + data[0]] = data[1]['type']
			else:
				# 有问题
				# 需要将'type'为text的字段，在INDEXTYPE中变为....keyword
				if data[1]['type'] == 'text':
					Keyword_type[prefix + data[0] + '.keyword'] = data[1]['type']
				else:
					Keyword_type[prefix + data[0]] = data[1]['type']

				data[1]['type'] = "String"
				String_type[prefix + data[0]] = data[1]['type']
				if prefix == '':
					String_first_type[prefix + data[0]] = data[1]['type']
			temp[data[0]] = data[1]['type']
		else:
			temp[data[0]] = format_mappings(prefix + data[0] + ".", data[1])
	return temp


# 获得INDEX_fields所需的字段数组
def get_INDEX_fields(index, data_type):
	temp = {}
	for data in data_type.items():
		if type(data[1]) != dict:
			if data[1] == 'Float':
				temp[data[0]] = "Float"
			elif data[1] == 'Int':
				temp[data[0]] = "Int"
			else:
				temp[data[0]] = "String"
		else:
			temp[data[0]] = index + "_" + data[0] + '_' +"fields"
			get_INDEX_fields(index + "_" + data[0], data[1])
	INDEX_fields[index + '_fields'] = temp


# INDEX_type
def index_type(INDEX, INDEXType):
	temp = ''
	for i in INDEXType:
		temp += "  %s\n" % i
	if temp == '':
		return 'enum %sType{\n  none\n}\n' % INDEX
	str = 'enum %sType{\n%s}\n' % (INDEX, temp)
	return str


# INDEX_num_type
def index_num_type(INDEX, INDEXNumType):
	temp = ''
	for i in INDEXNumType:
		temp += "  %s\n" % i
	if temp == '':
		return 'enum %sNumType{\n  none\n}\n' % INDEX
	str = 'enum %sNumType{\n%s}\n' % (INDEX, temp)
	return str


# INDEX_match and sort
def index_match_and_sort(INDEX, INDEXMatch):
	temp = ''
	for i in INDEXMatch.items():
		temp += '  %s : %s\n' % (i[0], i[1])
	temp2 = ''
	for i in INDEXMatch.items():
		temp2 += '  %s : [order_type]\n' % i[0]
	if temp == '':
		return 'input %sMatch{\n  none:String\n}\ninput %sSort{\n  none:String\n}\n' % (INDEX, INDEX)
	str = 'input %sMatch{\n%s}\ninput %sSort{\n%s}\n' % (INDEX, temp, INDEX, temp2)
	return str


# INDEX_range
def index_range(INDEX, INDEXRange):
	temp = ''
	for i in INDEXRange.items():
		temp += '  %s : %s\n' % (i[0], i[1])
	if temp == '':
		return 'input %sRange{\n  none:String\n}\n' % INDEX
	str = 'input %sRange{\n%s}\n' % (INDEX, temp)
	return str


# INDEX_fields
def get_index_field(INDEXOBJECT_FIELD):
	temp = ''
	for i in INDEXOBJECT_FIELD[1].items():
		temp += '  %s : %s\n' % (i[0], i[1])
	if temp == '':
		return 'type %s {\n  none:String\n}\n' % temp
	str = 'type %s {\n%s}\n' % (INDEXOBJECT_FIELD[0], temp)
	return str


def get_index_fields(INDEX_fields):
	str = ''
	for i in INDEX_fields.items():
		str += get_index_field(i)
	return str


def extract_field(INDEX, mappings):
	# 去type
	
	mappings = mappings['mappings']
	data_type = format_mappings('', mappings)
	get_INDEX_fields(INDEX, data_type)
	INDEXMatch = {**Num_first_type, **String_first_type}
	INDEXRange = Num_first_type
	INDEXType = list(Num_first_type.keys()) + list(String_first_type.keys())
	INDEXNumType = list(Num_first_type.keys())
	change_str = "\n" + index_type(INDEX, INDEXType) + index_num_type(INDEX, INDEXNumType) + index_match_and_sort(INDEX, INDEXMatch) + index_range(INDEX, INDEXRange) + get_index_fields(INDEX_fields)
	
	# 辅助字段提示
	string_type = list(Keyword_type.keys())
	num_type = list(Num_type.keys())
	INDEX_fields.clear()
	print('extract_field:finished\n')
	return change_str, string_type, num_type

# 
# INDEX = 'squint_domain'
# mappings = {"mappings" : {
#       "properties" : {
#         "cert_hash" : {
#           "type" : "keyword"
#         },
#         "create_timestamp" : {
#           "type" : "date",
#           "format" : "yyyy-MM-dd HH:mm:ss"
#         },
#         "domain" : {
#           "type" : "text",
#           "fields" : {
#             "keyword" : {
#               "type" : "keyword",
#               "ignore_above" : 256
#             }
#           },
#           "analyzer" : "ik_max_word"
#         },
#         "icp" : {
#           "properties" : {
#             "collected_timestamp" : {
#               "type" : "date",
#               "format" : "yyyy-MM-dd HH:mm:ss"
#             },
#             "domain_id" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               }
#             },
#             "home_url" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "leader_name" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               }
#             },
#             "limit_access" : {
#               "type" : "keyword"
#             },
#             "main_id" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               }
#             },
#             "main_licence" : {
#               "type" : "keyword"
#             },
#             "service_id" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               }
#             },
#             "service_licence" : {
#               "type" : "keyword"
#             },
#             "service_name" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "unit_name" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "unit_type" : {
#               "type" : "keyword"
#             },
#             "update_record_time" : {
#               "type" : "keyword"
#             }
#           }
#         },
#         "main_domain" : {
#           "type" : "boolean"
#         },
#         "psr" : {
#           "properties" : {
#             "collected_timestamp" : {
#               "type" : "date",
#               "format" : "yyyy-MM-dd HH:mm:ss"
#             },
#             "record_bureau" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "record_id" : {
#               "type" : "keyword"
#             },
#             "record_time" : {
#               "type" : "keyword"
#             },
#             "unit_name" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "unit_type" : {
#               "type" : "keyword"
#             },
#             "website_main_domain" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "website_name" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "website_second_domain" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "website_type" : {
#               "type" : "keyword"
#             }
#           }
#         },
#         "rr" : {
#           "properties" : {
#             "A" : {
#               "properties" : {
#                 "accuracy" : {
#                   "type" : "keyword"
#                 },
#                 "areacode" : {
#                   "type" : "keyword"
#                 },
#                 "asnumber" : {
#                   "type" : "keyword"
#                 },
#                 "city" : {
#                   "type" : "keyword"
#                 },
#                 "continent" : {
#                   "type" : "keyword"
#                 },
#                 "country" : {
#                   "type" : "keyword"
#                 },
#                 "district" : {
#                   "type" : "keyword"
#                 },
#                 "ip" : {
#                   "type" : "keyword"
#                 },
#                 "isp" : {
#                   "type" : "keyword"
#                 },
#                 "latbd" : {
#                   "type" : "float"
#                 },
#                 "latwgs" : {
#                   "type" : "float"
#                 },
#                 "lngbd" : {
#                   "type" : "float"
#                 },
#                 "lngwgs" : {
#                   "type" : "float"
#                 },
#                 "prov" : {
#                   "type" : "keyword"
#                 },
#                 "radius" : {
#                   "type" : "keyword"
#                 }
#               }
#             },
#             "AAAA" : {
#               "type" : "keyword"
#             },
#             "CNAME" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "MX" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "NS" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             },
#             "TXT" : {
#               "type" : "text",
#               "fields" : {
#                 "keyword" : {
#                   "type" : "keyword",
#                   "ignore_above" : 256
#                 }
#               },
#               "analyzer" : "ik_max_word"
#             }
#           }
#         },
#         "snapshot" : {
#           "properties" : {
#             "classification" : {
#               "properties" : {
#                 "probability" : {
#                   "type" : "float"
#                 },
#                 "type" : {
#                   "type" : "keyword"
#                 }
#               }
#             },
#             "collected_timestamp" : {
#               "type" : "date"
#             },
#             "meta" : {
#               "properties" : {
#                 "classifier_version" : {
#                   "type" : "keyword"
#                 },
#                 "location" : {
#                   "type" : "keyword"
#                 },
#                 "snapshot_version" : {
#                   "type" : "keyword"
#                 }
#               }
#             },
#             "request" : {
#               "properties" : {
#                 "domain" : {
#                   "type" : "keyword"
#                 },
#                 "main_domain" : {
#                   "type" : "keyword"
#                 },
#                 "request_url" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "scheme" : {
#                   "type" : "keyword"
#                 }
#               }
#             },
#             "response" : {
#               "properties" : {
#                 "cert_hash" : {
#                   "type" : "keyword"
#                 },
#                 "external_urls" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "favicon" : {
#                   "properties" : {
#                     "img_url" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     },
#                     "md5" : {
#                       "type" : "keyword"
#                     }
#                   }
#                 },
#                 "frame" : {
#                   "properties" : {
#                     "child_frames" : {
#                       "properties" : {
#                         "child_frames" : {
#                           "properties" : {
#                             "child_frames" : {
#                               "properties" : {
#                                 "child_frames" : {
#                                   "properties" : {
#                                     "child_frames" : {
#                                       "properties" : {
#                                         "frame_url" : {
#                                           "type" : "text",
#                                           "fields" : {
#                                             "keyword" : {
#                                               "type" : "keyword",
#                                               "ignore_above" : 256
#                                             }
#                                           }
#                                         },
#                                         "html_url" : {
#                                           "type" : "text",
#                                           "fields" : {
#                                             "keyword" : {
#                                               "type" : "keyword",
#                                               "ignore_above" : 256
#                                             }
#                                           }
#                                         },
#                                         "text_content_url" : {
#                                           "type" : "text",
#                                           "fields" : {
#                                             "keyword" : {
#                                               "type" : "keyword",
#                                               "ignore_above" : 256
#                                             }
#                                           }
#                                         }
#                                       }
#                                     },
#                                     "frame_url" : {
#                                       "type" : "text",
#                                       "fields" : {
#                                         "keyword" : {
#                                           "type" : "keyword",
#                                           "ignore_above" : 256
#                                         }
#                                       }
#                                     },
#                                     "html_url" : {
#                                       "type" : "text",
#                                       "fields" : {
#                                         "keyword" : {
#                                           "type" : "keyword",
#                                           "ignore_above" : 256
#                                         }
#                                       }
#                                     },
#                                     "text_content_url" : {
#                                       "type" : "text",
#                                       "fields" : {
#                                         "keyword" : {
#                                           "type" : "keyword",
#                                           "ignore_above" : 256
#                                         }
#                                       }
#                                     }
#                                   }
#                                 },
#                                 "frame_url" : {
#                                   "type" : "text",
#                                   "fields" : {
#                                     "keyword" : {
#                                       "type" : "keyword",
#                                       "ignore_above" : 256
#                                     }
#                                   }
#                                 },
#                                 "html_url" : {
#                                   "type" : "text",
#                                   "fields" : {
#                                     "keyword" : {
#                                       "type" : "keyword",
#                                       "ignore_above" : 256
#                                     }
#                                   }
#                                 },
#                                 "text_content_url" : {
#                                   "type" : "text",
#                                   "fields" : {
#                                     "keyword" : {
#                                       "type" : "keyword",
#                                       "ignore_above" : 256
#                                     }
#                                   }
#                                 }
#                               }
#                             },
#                             "frame_url" : {
#                               "type" : "text",
#                               "fields" : {
#                                 "keyword" : {
#                                   "type" : "keyword",
#                                   "ignore_above" : 256
#                                 }
#                               }
#                             },
#                             "html_url" : {
#                               "type" : "text",
#                               "fields" : {
#                                 "keyword" : {
#                                   "type" : "keyword",
#                                   "ignore_above" : 256
#                                 }
#                               }
#                             },
#                             "text_content_url" : {
#                               "type" : "text",
#                               "fields" : {
#                                 "keyword" : {
#                                   "type" : "keyword",
#                                   "ignore_above" : 256
#                                 }
#                               }
#                             }
#                           }
#                         },
#                         "frame_url" : {
#                           "type" : "text",
#                           "fields" : {
#                             "keyword" : {
#                               "type" : "keyword",
#                               "ignore_above" : 256
#                             }
#                           }
#                         },
#                         "html_url" : {
#                           "type" : "text",
#                           "fields" : {
#                             "keyword" : {
#                               "type" : "keyword",
#                               "ignore_above" : 256
#                             }
#                           }
#                         },
#                         "text_content_url" : {
#                           "type" : "text",
#                           "fields" : {
#                             "keyword" : {
#                               "type" : "keyword",
#                               "ignore_above" : 256
#                             }
#                           }
#                         }
#                       }
#                     },
#                     "description" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     },
#                     "frame_url" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     },
#                     "html_url" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     },
#                     "icp" : {
#                       "type" : "keyword"
#                     },
#                     "keywords" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     },
#                     "text_content_url" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     },
#                     "title" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     }
#                   }
#                 },
#                 "remote_address" : {
#                   "properties" : {
#                     "accuracy" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "areacode" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "asnumber" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "city" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "continent" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "country" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "district" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "ip" : {
#                       "type" : "keyword"
#                     },
#                     "isp" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "latbd" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "latwgs" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "lngbd" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "lngwgs" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "port" : {
#                       "type" : "integer"
#                     },
#                     "prov" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     },
#                     "radius" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       }
#                     }
#                   }
#                 },
#                 "response_url" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "snapshot_url" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             }
#           }
#         },
#         "subdomains" : {
#           "type" : "text",
#           "fields" : {
#             "keyword" : {
#               "type" : "keyword",
#               "ignore_above" : 256
#             }
#           },
#           "analyzer" : "ik_max_word"
#         },
#         "tags" : {
#           "type" : "keyword"
#         },
#         "update_timestamp" : {
#           "type" : "date",
#           "format" : "yyyy-MM-dd HH:mm:ss"
#         },
#         "web" : {
#           "properties" : {
#             "http" : {
#               "properties" : {
#                 "body" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   }
#                 },
#                 "cert_hash" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   }
#                 },
#                 "description" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "headers" : {
#                   "properties" : {
#                     "key" : {
#                       "type" : "keyword"
#                     },
#                     "value" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     }
#                   }
#                 },
#                 "keywords" : {
#                   "type" : "keyword"
#                 },
#                 "server" : {
#                   "type" : "keyword"
#                 },
#                 "status_code" : {
#                   "type" : "integer"
#                 },
#                 "title" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "url" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             },
#             "https" : {
#               "properties" : {
#                 "cert_hash" : {
#                   "type" : "keyword"
#                 },
#                 "description" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "headers" : {
#                   "properties" : {
#                     "key" : {
#                       "type" : "keyword"
#                     },
#                     "value" : {
#                       "type" : "text",
#                       "fields" : {
#                         "keyword" : {
#                           "type" : "keyword",
#                           "ignore_above" : 256
#                         }
#                       },
#                       "analyzer" : "ik_max_word"
#                     }
#                   }
#                 },
#                 "keywords" : {
#                   "type" : "keyword"
#                 },
#                 "server" : {
#                   "type" : "keyword"
#                 },
#                 "status_code" : {
#                   "type" : "integer"
#                 },
#                 "title" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "url" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             }
#           }
#         },
#         "whois" : {
#           "properties" : {
#             "administrator" : {
#               "properties" : {
#                 "city" : {
#                   "type" : "keyword"
#                 },
#                 "country" : {
#                   "type" : "keyword"
#                 },
#                 "email" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "fax" : {
#                   "type" : "keyword"
#                 },
#                 "fax_extension" : {
#                   "type" : "keyword"
#                 },
#                 "id" : {
#                   "type" : "keyword"
#                 },
#                 "name" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "organization" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "phone" : {
#                   "type" : "keyword"
#                 },
#                 "phone_extension" : {
#                   "type" : "keyword"
#                 },
#                 "postal_code" : {
#                   "type" : "keyword"
#                 },
#                 "province" : {
#                   "type" : "keyword"
#                 },
#                 "street" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             },
#             "billing" : {
#               "properties" : {
#                 "city" : {
#                   "type" : "keyword"
#                 },
#                 "country" : {
#                   "type" : "keyword"
#                 },
#                 "email" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "fax" : {
#                   "type" : "keyword"
#                 },
#                 "fax_extension" : {
#                   "type" : "keyword"
#                 },
#                 "id" : {
#                   "type" : "keyword"
#                 },
#                 "name" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "organization" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "phone" : {
#                   "type" : "keyword"
#                 },
#                 "phone_extension" : {
#                   "type" : "keyword"
#                 },
#                 "postal_code" : {
#                   "type" : "keyword"
#                 },
#                 "province" : {
#                   "type" : "keyword"
#                 },
#                 "street" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             },
#             "collected_timestamp" : {
#               "type" : "date",
#               "format" : "yyyy-MM-dd HH:mm:ss"
#             },
#             "domain_info" : {
#               "properties" : {
#                 "dns_sec" : {
#                   "type" : "keyword"
#                 },
#                 "name" : {
#                   "type" : "keyword"
#                 },
#                 "name_servers" : {
#                   "type" : "keyword"
#                 },
#                 "status" : {
#                   "type" : "keyword"
#                 }
#               }
#             },
#             "registrant" : {
#               "properties" : {
#                 "city" : {
#                   "type" : "keyword"
#                 },
#                 "country" : {
#                   "type" : "keyword"
#                 },
#                 "email" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "fax" : {
#                   "type" : "keyword"
#                 },
#                 "fax_extension" : {
#                   "type" : "keyword"
#                 },
#                 "id" : {
#                   "type" : "keyword"
#                 },
#                 "name" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "organization" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "phone" : {
#                   "type" : "keyword"
#                 },
#                 "phone_extension" : {
#                   "type" : "keyword"
#                 },
#                 "postal_code" : {
#                   "type" : "keyword"
#                 },
#                 "province" : {
#                   "type" : "keyword"
#                 },
#                 "street" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             },
#             "registrar" : {
#               "properties" : {
#                 "email" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "iana_id" : {
#                   "type" : "keyword"
#                 },
#                 "name" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "phone" : {
#                   "type" : "keyword"
#                 },
#                 "website" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "whois_servers" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             },
#             "registry" : {
#               "properties" : {
#                 "creation_time" : {
#                   "type" : "date"
#                 },
#                 "domain_id" : {
#                   "type" : "keyword"
#                 },
#                 "expiration_time" : {
#                   "type" : "date"
#                 },
#                 "updated_time" : {
#                   "type" : "date"
#                 }
#               }
#             },
#             "technician" : {
#               "properties" : {
#                 "city" : {
#                   "type" : "keyword"
#                 },
#                 "country" : {
#                   "type" : "keyword"
#                 },
#                 "email" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "fax" : {
#                   "type" : "keyword"
#                 },
#                 "fax_extension" : {
#                   "type" : "keyword"
#                 },
#                 "id" : {
#                   "type" : "keyword"
#                 },
#                 "name" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "organization" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 },
#                 "phone" : {
#                   "type" : "keyword"
#                 },
#                 "phone_extension" : {
#                   "type" : "keyword"
#                 },
#                 "postal_code" : {
#                   "type" : "keyword"
#                 },
#                 "province" : {
#                   "type" : "keyword"
#                 },
#                 "street" : {
#                   "type" : "text",
#                   "fields" : {
#                     "keyword" : {
#                       "type" : "keyword",
#                       "ignore_above" : 256
#                     }
#                   },
#                   "analyzer" : "ik_max_word"
#                 }
#               }
#             }
#           }
#         }
#       }
#     }
# }
# a, b, c = extract_field(INDEX, mappings)
# print(a)
# print(b)
# print(c)

