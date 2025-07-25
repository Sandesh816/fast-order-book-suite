# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: order.proto
# Protobuf Python Version: 6.31.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    6,
    31,
    0,
    '',
    'order.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0border.proto\x12\x06\x66\x61stob\"c\n\tOrderMeta\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x18\n\x10gateway_order_id\x18\x02 \x01(\t\x12\x14\n\x0crecv_unix_ns\x18\x03 \x01(\x03\x12\x13\n\x0brisk_status\x18\x04 \x01(\t\"Y\n\nLimitOrder\x12\x0e\n\x06is_buy\x18\x01 \x01(\x08\x12\r\n\x05price\x18\x02 \x01(\x05\x12\x0b\n\x03qty\x18\x03 \x01(\x05\x12\x1f\n\x04meta\x18\n \x01(\x0b\x32\x11.fastob.OrderMeta\"K\n\x0bMarketOrder\x12\x0e\n\x06is_buy\x18\x01 \x01(\x08\x12\x0b\n\x03qty\x18\x02 \x01(\x05\x12\x1f\n\x04meta\x18\n \x01(\x0b\x32\x11.fastob.OrderMeta\"Z\n\x0b\x43\x61ncelOrder\x12\x0e\n\x06is_buy\x18\x01 \x01(\x08\x12\r\n\x05price\x18\x02 \x01(\x05\x12\x0b\n\x03qty\x18\x03 \x01(\x05\x12\x1f\n\x04meta\x18\n \x01(\x0b\x32\x11.fastob.OrderMeta\"S\n\x12SubmitLimitRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x0e\n\x06is_buy\x18\x02 \x01(\x08\x12\r\n\x05price\x18\x03 \x01(\x05\x12\x0b\n\x03qty\x18\x04 \x01(\x05\"E\n\x13SubmitMarketRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x0e\n\x06is_buy\x18\x02 \x01(\x08\x12\x0b\n\x03qty\x18\x03 \x01(\x05\"T\n\x13SubmitCancelRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\x12\x0e\n\x06is_buy\x18\x02 \x01(\x08\x12\r\n\x05price\x18\x03 \x01(\x05\x12\x0b\n\x03qty\x18\x04 \x01(\x05\"`\n\x03\x41\x63k\x12\n\n\x02ok\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x1f\n\x04meta\x18\x03 \x01(\x0b\x32\x11.fastob.OrderMeta\x12\x1b\n\x13\x65ngine_done_unix_ns\x18\x04 \x01(\x03\"\x0c\n\nTopRequest\".\n\x08TopReply\x12\x10\n\x08\x62\x65st_bid\x18\x01 \x01(\x05\x12\x10\n\x08\x62\x65st_ask\x18\x02 \x01(\x05\"\x0e\n\x0cStatsRequest\"\x9a\x01\n\nStatsReply\x12\x14\n\x0ctotal_orders\x18\x01 \x01(\x04\x12\x16\n\x0etotal_rejected\x18\x02 \x01(\x04\x12\x16\n\x0e\x61vg_latency_us\x18\x03 \x01(\x01\x12\x16\n\x0ep50_latency_us\x18\x04 \x01(\x01\x12\x16\n\x0ep95_latency_us\x18\x05 \x01(\x01\x12\x16\n\x0ep99_latency_us\x18\x06 \x01(\x01\"!\n\x0cResetRequest\x12\x11\n\tclient_id\x18\x01 \x01(\t\"\x18\n\nResetReply\x12\n\n\x02ok\x18\x01 \x01(\x08\x32\xbf\x01\n\x0e\x45ngineInternal\x12(\n\x05Limit\x12\x12.fastob.LimitOrder\x1a\x0b.fastob.Ack\x12*\n\x06Market\x12\x13.fastob.MarketOrder\x1a\x0b.fastob.Ack\x12*\n\x06\x43\x61ncel\x12\x13.fastob.CancelOrder\x1a\x0b.fastob.Ack\x12+\n\x03Top\x12\x12.fastob.TopRequest\x1a\x10.fastob.TopReply2\xce\x02\n\rGatewayPublic\x12\x36\n\x0bSubmitLimit\x12\x1a.fastob.SubmitLimitRequest\x1a\x0b.fastob.Ack\x12\x38\n\x0cSubmitMarket\x12\x1b.fastob.SubmitMarketRequest\x1a\x0b.fastob.Ack\x12\x38\n\x0cSubmitCancel\x12\x1b.fastob.SubmitCancelRequest\x1a\x0b.fastob.Ack\x12+\n\x03Top\x12\x12.fastob.TopRequest\x1a\x10.fastob.TopReply\x12\x31\n\x05Stats\x12\x14.fastob.StatsRequest\x1a\x12.fastob.StatsReply\x12\x31\n\x05Reset\x12\x14.fastob.ResetRequest\x1a\x12.fastob.ResetReplyB\nZ\x08\x66\x61stobpbb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'order_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z\010fastobpb'
  _globals['_ORDERMETA']._serialized_start=23
  _globals['_ORDERMETA']._serialized_end=122
  _globals['_LIMITORDER']._serialized_start=124
  _globals['_LIMITORDER']._serialized_end=213
  _globals['_MARKETORDER']._serialized_start=215
  _globals['_MARKETORDER']._serialized_end=290
  _globals['_CANCELORDER']._serialized_start=292
  _globals['_CANCELORDER']._serialized_end=382
  _globals['_SUBMITLIMITREQUEST']._serialized_start=384
  _globals['_SUBMITLIMITREQUEST']._serialized_end=467
  _globals['_SUBMITMARKETREQUEST']._serialized_start=469
  _globals['_SUBMITMARKETREQUEST']._serialized_end=538
  _globals['_SUBMITCANCELREQUEST']._serialized_start=540
  _globals['_SUBMITCANCELREQUEST']._serialized_end=624
  _globals['_ACK']._serialized_start=626
  _globals['_ACK']._serialized_end=722
  _globals['_TOPREQUEST']._serialized_start=724
  _globals['_TOPREQUEST']._serialized_end=736
  _globals['_TOPREPLY']._serialized_start=738
  _globals['_TOPREPLY']._serialized_end=784
  _globals['_STATSREQUEST']._serialized_start=786
  _globals['_STATSREQUEST']._serialized_end=800
  _globals['_STATSREPLY']._serialized_start=803
  _globals['_STATSREPLY']._serialized_end=957
  _globals['_RESETREQUEST']._serialized_start=959
  _globals['_RESETREQUEST']._serialized_end=992
  _globals['_RESETREPLY']._serialized_start=994
  _globals['_RESETREPLY']._serialized_end=1018
  _globals['_ENGINEINTERNAL']._serialized_start=1021
  _globals['_ENGINEINTERNAL']._serialized_end=1212
  _globals['_GATEWAYPUBLIC']._serialized_start=1215
  _globals['_GATEWAYPUBLIC']._serialized_end=1549
# @@protoc_insertion_point(module_scope)
