from datetime import datetime
from typing import Optional

from sqlmodel import Field
from sqlmodel import SQLModel


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
    event_time: Optional[datetime]
    gateway_id: Optional[str]
    gateway_eui: Optional[str]
    connected_at: Optional[datetime]
    protocol: Optional[str]
    last_status_received_at: Optional[datetime]
    last_status_time: Optional[datetime]
    last_uplink_received_at: Optional[datetime]
    last_downlink_received_at: Optional[datetime]
    boot_time: Optional[datetime]
    ttn_lw_gateway_server: Optional[str]
    fpga: Optional[str]
    hal: Optional[str]
    latitude: Optional[datetime]
    longitude: Optional[str]
    altitude: Optional[float]
    source: Optional[str]
    ip: Optional[str]
    txin: Optional[str]
    txok: Optional[str]
    lpps: Optional[str]
    rxin: Optional[str]
    rxok: Optional[str]
    rxfw: Optional[str]
    ackr: Optional[str]
    uplink_count: Optional[int]
    downlink_count: Optional[int]
    min_round_trip_times: Optional[str]
    max_round_trip_times: Optional[str]
    median_round_trip_times: Optional[str]
    count_round_trip_times: Optional[str]
    min_freq_band_0: Optional[str]
    max_freq_band_0: Optional[str]
    dl_utilization_limit_band_0: Optional[str]
    min_freq_band_1: Optional[str]
    max_freq_band_1: Optional[str]
    dl_utilization_limit_band_1: Optional[str]
    dl_utilization_band_1: Optional[str]
    min_freq_band_2: Optional[str]
    max_freq_band_2: Optional[str]
    dl_utilization_limit_band_2: Optional[str]
    dl_utilization_band_2: Optional[str]
    min_freq_band_3: Optional[str]
    max_freq_band_3: Optional[str]
    dl_utilization_limit_band_3: Optional[str]
    min_freq_band_4: Optional[str]
    max_freq_band_4: Optional[str]
    dl_utilization_limit_band_4: Optional[str]
    min_freq_band_5: Optional[str]
    max_freq_band_5: Optional[str]
    dl_utilization_limit_band_5: Optional[str]


class AllRelation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: Optional[str] = None
    dev_addr: Optional[str] = None
    last_f_cnt: Optional[str] = None
    application_id: Optional[str] = None
    gateway_tti_id: Optional[str] = None


class MonitoredGateways(SQLModel, table=True):
    gateway_id_tti: Optional[str] = Field(primary_key=True)


class EndDeviceKPIs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    interval_start_time: datetime = Field(index=True)
    interval_end_time: datetime = Field(index=True)
    device_id: str = Field(index=True)
    gateway_id: str = Field(index=True)
    sampling_rate: Optional[float] = None
    total_dl_pkt_count: Optional[int] = None
    total_ul_pkt_count: Optional[int] = None
    total_unique_ul_count: Optional[int] = None
    total_packet_loss: Optional[int] = None
    total_packet_loss_ratio: Optional[float] = None
    missing_f_cnt_count: Optional[int] = None
    missing_f_cnt_ratio: Optional[float] = None
    replica_1_count: Optional[int] = None
    replica_1_ratio: Optional[float] = None
    replica_2_count: Optional[int] = None
    replica_2_ratio: Optional[float] = None
    replica_3_count: Optional[int] = None
    replica_3_ratio: Optional[float] = None
    gw_total_packet_loss: Optional[int] = None
    gw_total_packet_loss_ratio: Optional[float] = None
    gw_missing_f_cnt_count: Optional[int] = None
    gw_missing_f_cnt_ratio: Optional[float] = None
    gw_replica_1_count: Optional[int] = None
    gw_replica_1_ratio: Optional[float] = None
    gw_replica_2_count: Optional[int] = None
    gw_replica_2_ratio: Optional[float] = None
    gw_replica_3_count: Optional[int] = None
    gw_replica_3_ratio: Optional[float] = None
    consumed_duty_cycle: Optional[float] = None
    snr_mean: Optional[float] = None
    snr_variance: Optional[float] = None
    rssi_mean: Optional[float] = None
    rssi_variance: Optional[float] = None
    payload_size_mean: Optional[float] = None
    payload_size_variance: Optional[float] = None
    toa_mean: Optional[float] = None
    toa_variance: Optional[float] = None

    spreading_factor_distribution: Optional[str] = None
    spreading_factor_ratios: Optional[str] = None
    frequency_distribution: Optional[str] = None
    frequency_ratios: Optional[str] = None


class GatewayKPIs(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    interval_start_time: Optional[datetime] = Field(index=True)
    interval_end_time: Optional[datetime] = Field(index=True)
    gateway_id: Optional[str] = Field(index=True)
    total_dl_pkt_count: Optional[int] = None
    total_ul_pkt_count: Optional[int] = None
    total_packet_loss: Optional[int] = None
    total_packet_loss_ratio: Optional[float] = None
    missing_f_cnt_count: Optional[int] = None
    missing_f_cnt_ratio: Optional[float] = None
    replica_1_count: Optional[int] = None
    replica_1_ratio: Optional[float] = None
    replica_2_count: Optional[int] = None
    replica_2_ratio: Optional[float] = None
    replica_3_count: Optional[int] = None
    replica_3_ratio: Optional[float] = None
    num_active_connected_node: Optional[float] = None
    num_active_reg_connected_node: Optional[float] = None
    num_active_not_reg_connected_node: Optional[float] = None
    gw_utilization: Optional[float] = None
    total_consumed_airtime: Optional[float] = None
    availability: Optional[float] = None
    latency: Optional[float] = None
    jitter_mean: Optional[float] = None
    jitter_std_dev: Optional[float] = None
    snr_mean: Optional[float] = None
    snr_variance: Optional[float] = None
    rssi_mean: Optional[float] = None
    rssi_variance: Optional[float] = None
    payload_size_mean: Optional[float] = None
    payload_size_variance: Optional[float] = None
    toa_mean: Optional[float] = None
    toa_variance: Optional[float] = None
    spreading_factor_distribution: Optional[dict[str, int]] = None
    spreading_factor_ratios: Optional[dict[str, float]] = None
    frequency_distribution: Optional[dict[str, int]] = None
    frequency_ratios: Optional[dict[str, float]] = None
