from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PacketReplicaMetadata(SQLModel, table=True):
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
    device_id: Optional[str]
    dev_addr: Optional[str]
    gateway_id: Optional[str]
    f_cnt: Optional[int]
    received_at_gw: Optional[datetime]
    num_rx_replica: Optional[int]
    num_loss_replica: Optional[int]
    tot_rx_replica: Optional[int]
    tot_loss_replica: Optional[int]
    num_gws: Optional[int]


class NodeMetadataUl(SQLModel, table=True):
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
    dev_addr: Optional[str]
    device_id: Optional[str]
    join_eui: Optional[str]
    dev_eui: Optional[str]
    application_id: Optional[str] = None
    received_at: Optional[str]
    f_port: Optional[str]
    f_cnt: Optional[int]
    f_ctrl_adr: Optional[str]
    frm_payload: Optional[str]
    gateway_id: Optional[str]
    gateway_eui: Optional[str]
    rssi: Optional[float]
    channel_rssi: Optional[float]
    snr: Optional[float]
    channel_index: Optional[str]
    bandwidth: Optional[str]
    spreading_factor: Optional[str]
    coding_rate: Optional[str]
    frequency: Optional[str]
    consumed_airtime: Optional[str]
    payload_size: Optional[float]
    m_type: Optional[str]
    dev_nonce: Optional[str]
    gps_time: Optional[str]
    timestamp: Optional[str]
    time: Optional[datetime]
    event_time: Optional[datetime]
    received_at_gw: Optional[datetime]
    received_at_tti: Optional[datetime]


class NodeMetadataDl(SQLModel, table=True):
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


class GatewayStatusReceive(SQLModel, table=True):
    """
    This model represents the status of a gateway at the time it received a packet.

    Fields:
        id (int, optional): The ID of the status record.
        event_time (datetime): The time when the gateway status was received.
        gateway_id (str): The ID of the gateway.
        gateway_eui (str): The EUI of the gateway.
        time (datetime): The time of the gateway's internal clock.
        boot_time (datetime): The time when the gateway last booted.
        ttn_lw_gateway_server (str): The version of the TTN LoRaWAN Gateway Server running on the gateway.
        fpga (str): The version of the FPGA running on the gateway.
        hal (str): The version of the HAL (Hardware Abstraction Layer) running on the gateway.
        latitude (datetime): The latitude of the gateway.
        longitude (str): The longitude of the gateway.
        altitude (float): The altitude of the gateway.
        source (str): The source of the gateway status message.
        ip (str): The IP address of the gateway.
        txin (str): The number of transmitted packets that were received by the gateway.
        txok (str): The number of transmitted packets that were successfully transmitted by the gateway.
        lpps (str): The number of low-power periods per second for the gateway.
        rxin (str): The number of received packets that were received by the gateway.
        rxok (str): The number of received packets that were successfully received by the gateway.
        rxfw (str): The number of received packets that were forwarded by the gateway.
        ackr (str): The ACK (acknowledgement) rate of the gateway.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    event_time: Optional[datetime] = None
    gateway_id: Optional[str] = None
    gateway_eui: Optional[str] = None
    time: Optional[datetime] = None
    boot_time: Optional[datetime] = None
    ttn_lw_gateway_server: Optional[str] = None
    fpga: Optional[str] = None
    hal: Optional[str] = None
    latitude: Optional[datetime] = None
    longitude: Optional[str] = None
    altitude: Optional[float] = None
    source: Optional[str] = None
    ip: Optional[str] = None
    txin: Optional[str] = None
    txok: Optional[str] = None
    lpps: Optional[str] = None
    rxin: Optional[str] = None
    rxok: Optional[str] = None
    rxfw: Optional[str] = None
    ackr: Optional[str] = None


class GatewayConnectionStats(SQLModel, table=True):
    """
    This model represents the connection status metadata for a gateway.

    Fields:
        id (int, optional): The ID of the metadata record.
        event_time (datetime): The timestamp of when the connection status was received.
        gateway_id (str): The ID of the gateway.
        gateway_eui (str): The EUI of the gateway.
        connected_at (datetime): The timestamp of when the gateway connected.
        protocol (str): The protocol used by the gateway.
        last_status_received_at (datetime): The timestamp of when the last status was received.
        last_status_time (datetime): The timestamp of when the last status was updated.
        last_uplink_received_at (datetime): The timestamp of when the last uplink was received.
        last_downlink_received_at (datetime): The timestamp of when the last downlink was received.
        boot_time (datetime): The timestamp of when the gateway last booted.
        ttn_lw_gateway_server (str): The version of The Things Network's gateway server running on the gateway.
        fpga (str): The version of the FPGA on the gateway.
        hal (str): The version of the HAL on the gateway.
        latitude (datetime): The latitude of the gateway.
        longitude (str): The longitude of the gateway.
        altitude (float): The altitude of the gateway.
        source (str): The source of the connection status.
        ip (str): The IP address of the gateway.
        txin (str): The number of packets transmitted.
        txok (str): The number of packets successfully transmitted.
        lpps (str): The number of packets that went through LPPS.
        rxin (str): The number of packets received.
        rxok (str): The number of packets successfully received.
        rxfw (str): The number of packets forwarded.
        ackr (str): The percentage of ACKs received.
        uplink_count (int): The number of uplink messages received by the gateway.
        downlink_count (int): The number of downlink messages received by the gateway.
        min_round_trip_times (str): The minimum round trip time.
        max_round_trip_times (str): The maximum round trip time.
        median_round_trip_times (str): The median round trip time.
        count_round_trip_times (str): The number of round trip times.
        min_freq_band_0 (str): The minimum frequency in band 0.
        max_freq_band_0 (str): The maximum frequency in band 0.
        dl_utilization_limit_band_0 (str): The DL utilization limit for band 0.
        min_freq_band_1 (str): The minimum frequency in band 1.
        max_freq_band_1 (str): The maximum frequency in band 1.
        dl_utilization_limit_band_1 (str): The DL utilization limit for band 1.
        dl_utilization_band_1 (str): The DL utilization for band 1.
        min_freq_band_2 (str): The minimum frequency in band 2.
        max_freq_band_2 (str): The maximum frequency in band 2.
        dl_utilization_limit_band_2 (str): The DL utilization limit for band 2.
        dl_utilization_band_2 (str): The DL utilization for band 2.
        min_freq_band_3 (str): The minimum frequency in band 3.
        max_freq_band_3 (str): The maximum frequency in band 3.
        dl_utilization_limit_band_3 (str): The DL utilization limit for band 3.
        min_freq_band_4 (str, optional): The minimum frequency of band 4.
        max_freq_band_4 (str, optional): The maximum frequency of band 4.
        dl_utilization_limit_band_4 (str, optional): The downlink utilization limit of band 4.
        min_freq_band_5 (str, optional): The minimum frequency of band 5.
        max_freq_band_5 (str, optional): The maximum frequency of band 5.
        dl_utilization_limit_band_5 (str, optional): The downlink utilization limit of band 5.

    """

    id: Optional[int] = Field(default=None, primary_key=True)
    event_time: Optional[datetime] = None
    gateway_id: Optional[str] = None
    gateway_eui: Optional[str] = None
    connected_at: Optional[datetime] = None
    protocol: Optional[str] = None
    last_status_received_at: Optional[datetime] = None
    last_status_time: Optional[datetime] = None
    last_uplink_received_at: Optional[datetime] = None
    last_downlink_received_at: Optional[datetime] = None
    boot_time: Optional[datetime] = None
    ttn_lw_gateway_server: Optional[str] = None
    fpga: Optional[str] = None
    hal: Optional[str] = None
    latitude: Optional[datetime] = None
    longitude: Optional[str] = None
    altitude: Optional[float] = None
    source: Optional[str] = None
    ip: Optional[str] = None
    txin: Optional[str] = None
    txok: Optional[str] = None
    lpps: Optional[str] = None
    rxin: Optional[str] = None
    rxok: Optional[str] = None
    rxfw: Optional[str] = None
    ackr: Optional[str] = None
    uplink_count: Optional[int] = None
    downlink_count: Optional[int] = None
    min_round_trip_times: Optional[str] = None
    max_round_trip_times: Optional[str] = None
    median_round_trip_times: Optional[str] = None
    count_round_trip_times: Optional[str] = None
    min_freq_band_0: Optional[str] = None
    max_freq_band_0: Optional[str] = None
    dl_utilization_limit_band_0: Optional[str] = None
    min_freq_band_1: Optional[str] = None
    max_freq_band_1: Optional[str] = None
    dl_utilization_limit_band_1: Optional[str] = None
    dl_utilization_band_1: Optional[str] = None
    min_freq_band_2: Optional[str] = None
    max_freq_band_2: Optional[str] = None
    dl_utilization_limit_band_2: Optional[str] = None
    dl_utilization_band_2: Optional[str] = None
    min_freq_band_3: Optional[str] = None
    max_freq_band_3: Optional[str] = None
    dl_utilization_limit_band_3: Optional[str] = None
    min_freq_band_4: Optional[str] = None
    max_freq_band_4: Optional[str] = None
    dl_utilization_limit_band_4: Optional[str] = None
    min_freq_band_5: Optional[str] = None
    max_freq_band_5: Optional[str] = None
    dl_utilization_limit_band_5: Optional[str] = None


class DownlinkScheduleAttempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    time: Optional[datetime]
    gateway_id: Optional[str]
    gateway_eui: Optional[str]
    raw_payload: Optional[str]
    rx1_delay: Optional[int]
    rx1_data_rate_bandwidth: Optional[int]
    rx1_data_rate_spreading_factor: Optional[int]
    rx1_data_rate_coding_rate: Optional[str]
    rx1_frequency: Optional[str]
    rx2_data_rate_bandwidth: Optional[int]
    rx2_data_rate_spreading_factor: Optional[int]
    rx2_data_rate_coding_rate: Optional[str]
    rx2_frequency: Optional[str]
    priority: Optional[str]
    frequency_plan_id: Optional[str]
    origin: Optional[str]
    context_tenant_id: Optional[str]
    unique_id: Optional[str]

    @classmethod
    def from_json(cls, rx_event_message) -> Optional["DownlinkScheduleAttempt"]:
        data = rx_event_message.get("result", {}).get("data", {})
        request = data.get("request", {})
        rx1_data_rate = request.get("rx1_data_rate", {}).get("lora", {})
        rx2_data_rate = request.get("rx2_data_rate", {}).get("lora", {})
        gateway_ids = (
            rx_event_message.get("result", {}).get("identifiers", [])[0].get("gateway_ids", {})
        )
        try:
            return cls(
                time=datetime.fromisoformat(
                    rx_event_message.get("result", {}).get("time", "")[:-1]
                ),
                gateway_id=gateway_ids.get("gateway_id"),
                gateway_eui=gateway_ids.get("eui"),
                raw_payload=data.get("raw_payload"),
                rx1_delay=request.get("rx1_delay"),
                rx1_data_rate_bandwidth=rx1_data_rate.get("bandwidth"),
                rx1_data_rate_spreading_factor=rx1_data_rate.get("spreading_factor"),
                rx1_data_rate_coding_rate=rx1_data_rate.get("coding_rate"),
                rx1_frequency=request.get("rx1_frequency"),
                rx2_data_rate_bandwidth=rx2_data_rate.get("bandwidth"),
                rx2_data_rate_spreading_factor=rx2_data_rate.get("spreading_factor"),
                rx2_data_rate_coding_rate=rx2_data_rate.get("coding_rate"),
                rx2_frequency=request.get("rx2_frequency"),
                priority=request.get("priority"),
                frequency_plan_id=request.get("frequency_plan_id"),
                context_tenant_id=rx_event_message.get("result", {})
                .get("context", {})
                .get("tenant-id"),
                unique_id=rx_event_message.get("result", {}).get("unique_id"),
            )
        except (ValueError, TypeError):
            return None


class DownlinkTxAckReceive(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    time: Optional[str] = None
    gateway_id: Optional[str] = None
    gateway_eui: Optional[str] = None
    raw_payload: Optional[str] = None
    data_rate_bandwidth: Optional[int] = None
    data_rate_spreading_factor: Optional[int] = None
    data_rate_coding_rate: Optional[str] = None
    frequency: Optional[str] = None
    timestamp: Optional[int] = None
    tx_power: Optional[float] = None
    invert_polarization: Optional[bool] = None
    unique_id: Optional[str] = None

    @classmethod
    def from_json(cls, rx_event_message) -> "DownlinkTxAckReceive":
        data = rx_event_message["result"]["data"]
        downlink_message = data["downlink_message"]
        scheduled = downlink_message["scheduled"]

        return cls(
            time=data.get("time"),
            gateway_id=data["identifiers"][0]["gateway_ids"]["gateway_id"],
            gateway_eui=data["identifiers"][0]["gateway_ids"]["eui"],
            raw_payload=downlink_message["raw_payload"],
            data_rate_bandwidth=scheduled["data_rate"]["lora"]["bandwidth"],
            data_rate_spreading_factor=scheduled["data_rate"]["lora"]["spreading_factor"],
            data_rate_coding_rate=scheduled["data_rate"]["lora"]["coding_rate"],
            frequency=scheduled["frequency"],
            timestamp=scheduled["timestamp"],
            tx_power=scheduled["downlink"]["tx_power"],
            invert_polarization=scheduled["downlink"]["invert_polarization"],
            unique_id=data["unique_id"],
        )


class DifferentEvent(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    time: Optional[str] = None
    gateway_id: Optional[str] = None
    gateway_eui: Optional[str] = None
    context_tenant_id: Optional[str] = None
    unique_id: Optional[str] = None

    @classmethod
    def from_json(cls, rx_event_message):
        result = rx_event_message["result"]
        identifiers = result.get("identifiers", [{}])[0].get("gateway_ids", {})
        return cls(
            name=result["name"],
            time=result["time"],
            gateway_id=identifiers.get("gateway_id"),
            gateway_eui=identifiers.get("eui"),
            unique_id=result["unique_id"],
        )


class AllRelation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[str] = None
    dev_addr: Optional[str] = None
    last_f_cnt: Optional[str] = None
    application_id: Optional[str] = None
    gateway_tti_id: Optional[str] = None
