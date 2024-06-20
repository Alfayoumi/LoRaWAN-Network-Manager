import json
from datetime import datetime
from typing import List
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field
from sqlmodel import SQLModel


class PacketReplicaMetadata(SQLModel):
    """
    This model represents metadata for packets that were replicated and sent through a LoRaWAN network.

    Fields:
        id (int, optional): The ID of the metadata record.
        dev_addr (str): The device address of the end node that transmitted the packet.
        gateway_id (str): The ID of the gateway that received the packet.
        f_cnt (int): The frame counter of the packet.
        received_at_gw (datetime): The timestamp when the packet was received by the gateway.
        num_rx_replica (int): The number of times the packet was replicated.
        tot_rx_replica (int): The total number of replicas sent.
        tot_loss_replica (int): The number of replicas that were lost.
        num_gws (int): The number of gateways that received the packet.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    dev_addr: Optional[str] = None
    gateway_id: Optional[str] = None
    f_cnt: Optional[int] = None
    received_at_gw: Optional[datetime] = None
    num_rx_replica: Optional[int] = None
    tot_rx_replica: Optional[int] = None
    tot_loss_replica: Optional[int] = None
    num_gws: Optional[int] = None


class NodeMetadataUl(SQLModel):
    """
    This model represents metadata for an uplink message from a node in a LoRaWAN network.

    Fields:
        id (int, optional): The ID of the metadata record.
        dev_addr (str): The device address of the end node that transmitted the message.
        event_time (datetime): The timestamp when the message was generated.
        gateway_id (str): The ID of the gateway that received the message.
        gateway_eui (str): The EUI of the gateway that received the message.
        raw_payload (str): The raw payload of the message.
        m_type (str): The type of the message (JoinRequest, JoinAccept, UnconfirmedDataUp, etc.).
        f_ctrl_adr (str): The frame control and address of the message.
        f_cnt (int): The frame counter of the message.
        join_eui (str): The EUI of the join server for the node.
        dev_eui (str): The EUI of the end node.
        dev_nonce (str): The nonce value of the end node.
        frm_payload (str): The decrypted payload of the message.
        bandwidth (str): The bandwidth used for the transmission.
        spreading_factor (str): The spreading factor used for the transmission.
        coding_rate (str): The coding rate used for the transmission.
        frequency (str): The frequency used for the transmission.
        timestamp (str): The timestamp of the message, as a string.
        time (datetime): The timestamp of the message.
        rssi (float): The RSSI of the message.
        channel_rssi (float): The channel RSSI of the message.
        snr (float): The SNR of the message.
        channel_index (str): The channel index of the message.
        gps_time (str): The GPS timestamp of the message.
        received_at_gw (datetime): The timestamp when the message was received by the gateway.
        received_at_tti (datetime): The timestamp when the message was received by The Things Industries.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    dev_addr: Optional[str] = None
    device_id: Optional[str] = None
    join_eui: Optional[str] = None
    dev_eui: Optional[str] = None
    application_id: Optional[str] = None
    received_at: Optional[str] = None
    f_port: Optional[str] = None
    f_cnt: Optional[int] = None
    f_ctrl_adr: Optional[str] = None
    frm_payload: Optional[str] = None
    gateway_id: Optional[str] = None
    gateway_eui: Optional[str] = None
    rssi: Optional[float] = None
    channel_rssi: Optional[float] = None
    snr: Optional[float] = None
    channel_index: Optional[str] = None
    bandwidth: Optional[str] = None
    spreading_factor: Optional[str] = None
    coding_rate: Optional[str] = None
    frequency: Optional[str] = None
    consumed_airtime: Optional[str] = None
    payload_size: Optional[float] = None
    m_type: Optional[str] = None
    dev_nonce: Optional[str] = None
    gps_time: Optional[str] = None
    timestamp: Optional[str] = None
    time: Optional[datetime] = None
    event_time: Optional[datetime] = None
    received_at_gw: Optional[datetime] = None
    received_at_tti: Optional[datetime] = None


class NodeMetadataDl(SQLModel):
    """
    This model represents metadata for packets that were transmitted through a LoRaWAN network.

    Fields:
        id (int, optional): The ID of the metadata record.
        event_time (datetime): The timestamp when the packet was transmitted.
        gateway_id (str): The ID of the gateway that received the packet.
        gateway_eui (str): The EUI of the gateway that received the packet.
        raw_payload (str): The raw payload of the packet.
        bandwidth (str): The bandwidth used for transmitting the packet.
        spreading_factor (str): The spreading factor used for transmitting the packet.
        coding_rate (str): The coding rate used for transmitting the packet.
        frequency (str): The frequency used for transmitting the packet.
        timestamp (datetime): The timestamp of the packet.
        concentrator_timestamp (str): The concentrator timestamp of the packet.
        tx_power (float): The transmission power used for transmitting the packet.
        invert_polarization (str): The polarization of the transmission.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    event_time: Optional[datetime] = None
    gateway_id: Optional[str] = None
    gateway_eui: Optional[str] = None
    raw_payload: Optional[str] = None
    bandwidth: Optional[str] = None
    spreading_factor: Optional[str] = None
    coding_rate: Optional[str] = None
    frequency: Optional[str] = None
    timestamp: Optional[datetime] = None
    concentrator_timestamp: Optional[str] = None
    tx_power: Optional[float] = None
    invert_polarization: Optional[str] = None


class GatewayIds(BaseModel):
    gateway_id: Optional[str] = None
    eui: Optional[str] = None


class RxMetadata(BaseModel):
    gateway_ids: GatewayIds
    time: Optional[datetime] = None
    timestamp: Optional[str] = None
    rssi: Optional[float] = None
    channel_rssi: Optional[float] = None
    snr: Optional[float] = None
    channel_index: Optional[str] = None
    gps_time: Optional[str] = None
    received_at: Optional[datetime] = None


class TTIUplinkMessage(BaseModel):
    device_id: Optional[str] = None
    application_id: Optional[str] = None
    dev_eui: Optional[str] = None
    join_eui: Optional[str] = None
    dev_addr: Optional[str] = None
    received_at: Optional[str] = None
    f_port: Optional[str] = None
    f_cnt: Optional[int] = None
    frm_payload: Optional[str] = None
    rx_metadata: Optional[List[RxMetadata]] = None
    bandwidth: Optional[str] = None
    frequency: Optional[str] = None
    timestamp: Optional[str] = None
    gps_time: Optional[str] = None
    spreading_factor: Optional[str] = None
    coding_rate: Optional[str] = None
    time: Optional[str] = None
    consumed_airtime: Optional[str] = None

    @classmethod
    def from_json(cls, json_data):
        result = json_data
        rx_metadata = result.get("uplink_message", {}).get("rx_metadata", [])
        data_rate = result.get("uplink_message", {}).get("settings", {}).get("data_rate", {})

        return cls(
            device_id=result.get("end_device_ids", {}).get("device_id"),
            application_id=result.get("end_device_ids", {})
            .get("application_ids", {})
            .get("application_id"),
            dev_eui=result.get("end_device_ids", {}).get("dev_eui"),
            join_eui=result.get("end_device_ids", {}).get("join_eui"),
            dev_addr=result.get("end_device_ids", {}).get("dev_addr"),
            received_at=json_data.get("received_at"),
            f_port=result.get("uplink_message", {}).get("f_port"),
            f_cnt=result.get("uplink_message", {}).get("f_cnt"),
            frm_payload=result.get("uplink_message", {}).get("frm_payload"),
            rx_metadata=[
                RxMetadata(
                    gateway_ids=GatewayIds(
                        gateway_id=metadata.get("gateway_ids", {}).get("gateway_id"),
                        eui=metadata.get("gateway_ids", {}).get("eui"),
                    ),
                    time=metadata.get("time"),
                    timestamp=metadata.get("timestamp"),
                    rssi=metadata.get("rssi"),
                    channel_rssi=metadata.get("channel_rssi"),
                    snr=metadata.get("snr"),
                    channel_index=metadata.get("channel_index"),
                    gps_time=metadata.get("gps_time"),
                    received_at=metadata.get("received_at"),
                )
                for metadata in rx_metadata
            ],
            bandwidth=data_rate.get("bandwidth"),
            spreading_factor=data_rate.get("spreading_factor"),
            coding_rate=data_rate.get("coding_rate"),
            frequency=result.get("uplink_message", {}).get("settings", {}).get("frequency"),
            timestamp=result.get("uplink_message", {}).get("settings", {}).get("timestamp"),
            time=result.get("uplink_message", {}).get("settings", {}).get("time"),
            consumed_airtime=result.get("uplink_message", {}).get("consumed_airtime"),
        )


class AllRelation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[str] = None
    dev_addr: Optional[str] = None
    last_f_cnt: Optional[str] = None
    application_id: Optional[str] = None
    gateway_tti_id: Optional[str] = None
