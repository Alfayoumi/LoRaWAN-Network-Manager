import math
import os
import time
from collections import Counter
from datetime import datetime
from datetime import timedelta

from typing import Dict
from typing import List

import numpy as np
import schedule
from sqlalchemy import func
from sqlmodel import Session
from sqlmodel import select

from database.db import db_engine
from dependencies.exceptions import DatabaseError, ProcessError
from kpi_calculation.database.models import AllRelation
from kpi_calculation.database.models import EndDeviceKPIs
from kpi_calculation.database.models import GatewayConnectionStats
from kpi_calculation.database.models import GatewayKPIs
from kpi_calculation.database.models import MonitoredGateways
from kpi_calculation.database.models import NodeMetadataUl
from dependencies import utility_functions
from dependencies.config import logger_config
from dependencies.utility_functions import get_region_freq_plan
from dependencies.utility_functions import string_to_datetime


class EndDeviceKPICalculation:
    def __init__(self, engine, num_tx_replica, logger):
        self.db_engine = engine
        self.logger = logger
        self.num_tx_replica = num_tx_replica

    def get_unique_f_cnt_values(self, device_id, processed_till_time, interval_end_time):
        try:
            with Session(self.db_engine) as session:
                query = (
                    select(NodeMetadataUl.f_cnt, func.min(NodeMetadataUl.received_at_gw))
                    .where(
                        NodeMetadataUl.device_id == device_id,
                        NodeMetadataUl.received_at_gw >= processed_till_time,
                        NodeMetadataUl.received_at_gw < interval_end_time,
                    )
                    .group_by(NodeMetadataUl.f_cnt)
                    .order_by(NodeMetadataUl.f_cnt)
                )
                return session.exec(query).all()
        except Exception as e:
            self.logger.error(f"Error in get_unique_f_cnt_values: {str(e)}")
            raise DatabaseError("get_unique_f_cnt_values ",
                                f"Error in get_unique_f_cnt_values: {str(e)}")

    def get_all_f_cnt_for_device_in_gateway(
            self,
            device_id: str,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        try:
            with Session(self.db_engine) as session:
                query = select(NodeMetadataUl.f_cnt).where(
                    NodeMetadataUl.device_id == device_id,
                    NodeMetadataUl.gateway_id == gateway_id,
                    NodeMetadataUl.received_at_gw >= processed_till_time,
                    NodeMetadataUl.received_at_gw < interval_end_time,
                )
                return session.exec(query).all()
        except Exception as e:
            self.logger.error(f"Error in get_all_f_cnt_for_device_in_gateway: {str(e)}")
            raise DatabaseError("get_all_f_cnt_for_device_in_gateway ",
                                f"Error in get_all_f_cnt_for_device_in_gateway: {str(e)}")

    def get_all_data_for_device_in_gateway(
            self,
            device_id: str,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        try:
            with Session(self.db_engine) as session:
                query = select(NodeMetadataUl).where(
                    NodeMetadataUl.device_id == device_id,
                    NodeMetadataUl.gateway_id == gateway_id,
                    NodeMetadataUl.received_at_gw >= processed_till_time,
                    NodeMetadataUl.received_at_gw < interval_end_time,
                )
                return session.exec(query).all()
        except Exception as e:
            self.logger.error(f"Error in get_all_data_for_device_in_gateway: {str(e)}")
            raise DatabaseError("get_all_data_for_device_in_gateway ",
                                f"Error in get_all_data_for_device_in_gateway: {str(e)}")

    def get_all_f_cnt_for_device_in_all_gateways(
            self,
            device_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        try:
            # Get unique f_cnt values and data rows
            with Session(self.db_engine) as session:
                # Get all the packets based on the conditions
                query = select(NodeMetadataUl.f_cnt).where(
                    NodeMetadataUl.device_id == device_id,
                    NodeMetadataUl.received_at_gw >= processed_till_time,
                    NodeMetadataUl.received_at_gw < interval_end_time,
                )
                return session.exec(query).all()
        except Exception as e:
            self.logger.error(f"Error in get_all_f_cnt_for_device_in_all_gateways: {str(e)}")
            raise DatabaseError("get_all_f_cnt_for_device_in_all_gateways ",
                                f"Error in get_all_f_cnt_for_device_in_all_gateways: {str(e)}")

    def calculate_sampling_rate(self, device_id, processed_till_time, interval_end_time):
        try:
            self.logger.debug(f"calculate_sampling_rate device_id= {device_id}")
            data_rows = self.get_unique_f_cnt_values(device_id, processed_till_time, interval_end_time)
            self.logger.debug(f"data_rows data_rows= {data_rows}")
            data_rows = [row for row in data_rows if row[0] is not None]
            self.logger.debug(f"data_rows= {data_rows}")
            # Check if data_rows is empty
            if not data_rows:
                return None
            # Calculate time difference for each f_cnt value
            received_times = [row[1] for row in data_rows]
            f_cnt_values = [row[0] for row in data_rows]
            self.logger.debug(f"received_times = {received_times}")
            self.logger.debug(f"f_cnt_values = {f_cnt_values}")
            time_diffs = [
                (next_time - curr_time).total_seconds()
                for curr_time, next_time, curr_f_cnt, next_f_cnt in zip(
                    received_times, received_times[1:], f_cnt_values, f_cnt_values[1:]
                )
                if next_f_cnt - curr_f_cnt == 1
            ]
            self.logger.debug(f"time_diffs = {time_diffs}")
            # Calculate and return the average time difference
            if time_diffs:
                return math.floor(sum(time_diffs) / len(time_diffs))
            else:
                return None
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Failed calculate_sampling_rate: {str(e)}")
            raise ProcessError(f"Error calculate_sampling_rate: {repr(e)}") from e

    def get_total_uplink_messages(
            self,
            device_id: str,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ) -> int:
        try:

            with Session(self.db_engine) as session:
                """Get the total uplink messages for the device_id and gateway_id between
                processed_till_time and interval_end_time
                """
                query = select(NodeMetadataUl).where(
                    NodeMetadataUl.device_id == device_id,
                    NodeMetadataUl.gateway_id == gateway_id,
                    NodeMetadataUl.received_at_gw >= processed_till_time,
                    NodeMetadataUl.received_at_gw < interval_end_time,
                )
                result = session.exec(query).all()
                return len(result)

        except Exception as e:
            self.logger.error(f"Error in get_total_uplink_messages: {str(e)}")
            raise DatabaseError("get_total_uplink_messages ",
                                f"Error in get_total_uplink_messages: {str(e)}")

    def get_total_unique_uplink_messages(
            self,
            device_id: str,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ) -> int:
        try:
            with Session(self.db_engine) as session:
                query = (
                    select(NodeMetadataUl.f_cnt)
                    .where(
                        NodeMetadataUl.device_id == device_id,
                        NodeMetadataUl.gateway_id == gateway_id,
                        NodeMetadataUl.received_at_gw >= processed_till_time,
                        NodeMetadataUl.received_at_gw < interval_end_time,
                    )
                    .distinct()
                )

                result = session.exec(query).all()
                return len(result)

        except Exception as e:
            self.logger.error(f"Error in get_total_unique_uplink_messages: {str(e)}")
            raise DatabaseError("get_total_unique_uplink_messages ",
                                f"Error in get_total_unique_uplink_messages: {str(e)}")

    def calculate_total_pkt_loss_info_for_gateway(
            self,
            device_id: str,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        try:
            packets = self.get_all_f_cnt_for_device_in_gateway(device_id, gateway_id, processed_till_time,
                                                               interval_end_time)
            # Calculate the number of replicas for each f_cnt using Counter
            f_cnt_counts = Counter(packet for packet in packets)
            if not f_cnt_counts:
                return {
                    "total_packet_loss": 0,
                    "total_packet_loss_ratio": 0,
                    "missing_f_cnt_count": 0,
                    "missing_f_cnt_ratio": 0,
                    "replica_1_count": 0,
                    "replica_2_count": 0,
                    "replica_3_count": 0,
                    "replica_1_ratio": 0,
                    "replica_2_ratio": 0,
                    "replica_3_ratio": 0,
                }
            f_cnt_counts = {k: v for k, v in f_cnt_counts.items() if k is not None}
            if not f_cnt_counts:
                return None
            # Calculate the total packet loss
            total_packet_loss = sum(max(0, 3 - count) for count in f_cnt_counts.values())

            # Calculate replica distribution using dictionary comprehension
            replica_counts = [str(count) if count < 3 else "3" for count in f_cnt_counts.values()]
            replica_distribution = {
                "replica_1": replica_counts.count("1"),
                "replica_2": replica_counts.count("2"),
                "replica_3": replica_counts.count("3"),
            }

            # Add missing f_cnt values to the total packet loss
            min_f_cnt = min(f_cnt_counts)
            max_f_cnt = max(f_cnt_counts)
            total_unique_pkts = set(range(min_f_cnt, max_f_cnt + 1))
            missing_f_cnt_count = len(total_unique_pkts - set(f_cnt_counts.keys()))
            total_packet_loss += missing_f_cnt_count * 3

            # Calculate the ratio of the replica distribution
            total_f_cnt = sum(replica_distribution.values())
            replica_ratios = {
                "replica_1": replica_distribution["replica_1"] / total_f_cnt,
                "replica_2": replica_distribution["replica_2"] / total_f_cnt,
                "replica_3": replica_distribution["replica_3"] / total_f_cnt,
            }

            total_packet_loss_ratio = total_packet_loss / (len(total_unique_pkts) * 3)
            missing_f_cnt_ratio = missing_f_cnt_count / len(total_unique_pkts)

            return {
                "gw_total_packet_loss": total_packet_loss,
                "gw_total_packet_loss_ratio": total_packet_loss_ratio,
                "gw_missing_f_cnt_count": missing_f_cnt_count,
                "gw_missing_f_cnt_ratio": missing_f_cnt_ratio,
                "gw_replica_1_count": replica_distribution["replica_1"],
                "gw_replica_2_count": replica_distribution["replica_2"],
                "gw_replica_3_count": replica_distribution["replica_3"],
                "gw_replica_1_ratio": replica_ratios["replica_1"],
                "gw_replica_2_ratio": replica_ratios["replica_2"],
                "gw_replica_3_ratio": replica_ratios["replica_3"],
            }
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Failed calculate_total_pkt_loss_info_for_gateway: {str(e)}")
            raise ProcessError(f"Error calculate_total_pkt_loss_info_for_gateway: {repr(e)}") from e

    def calculate_total_pkt_loss_info(
            self,
            device_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        try:
            packets = self.get_all_f_cnt_for_device_in_all_gateways(device_id, processed_till_time, interval_end_time)
            self.logger.debug(f"packets = {packets}")
            # Calculate the number of replicas for each f_cnt using Counter
            f_cnt_counts = Counter(packet for packet in packets)
            if not f_cnt_counts:
                return {
                    "total_packet_loss": 0,
                    "total_packet_loss_ratio": 0,
                    "missing_f_cnt_count": 0,
                    "missing_f_cnt_ratio": 0,
                    "replica_1_count": 0,
                    "replica_2_count": 0,
                    "replica_3_count": 0,
                    "replica_1_ratio": 0,
                    "replica_2_ratio": 0,
                    "replica_3_ratio": 0,
                }
            f_cnt_counts = {k: v for k, v in f_cnt_counts.items() if k is not None}
            if not f_cnt_counts:
                return None
            # Calculate the total packet loss
            total_packet_loss = sum(max(0, 3 - count) for count in f_cnt_counts.values())

            # Calculate replica distribution using dictionary comprehension
            replica_counts = [str(count) if count < 3 else "3" for count in f_cnt_counts.values()]
            replica_distribution = {
                "replica_1": replica_counts.count("1"),
                "replica_2": replica_counts.count("2"),
                "replica_3": replica_counts.count("3"),
            }

            # Add missing f_cnt values to the total packet loss
            min_f_cnt = min(f_cnt_counts)
            max_f_cnt = max(f_cnt_counts)
            total_unique_pkts = set(range(min_f_cnt, max_f_cnt + 1))
            missing_f_cnt_count = len(total_unique_pkts - set(f_cnt_counts.keys()))
            total_packet_loss += missing_f_cnt_count * 3

            # Calculate the ratio of the replica distribution
            total_f_cnt = sum(replica_distribution.values())
            replica_ratios = {
                "replica_1": replica_distribution["replica_1"] / total_f_cnt,
                "replica_2": replica_distribution["replica_2"] / total_f_cnt,
                "replica_3": replica_distribution["replica_3"] / total_f_cnt,
            }

            total_packet_loss_ratio = total_packet_loss / (len(total_unique_pkts) * 3)
            missing_f_cnt_ratio = missing_f_cnt_count / len(total_unique_pkts)

            return {
                "total_packet_loss": total_packet_loss,
                "total_packet_loss_ratio": total_packet_loss_ratio,
                "missing_f_cnt_count": missing_f_cnt_count,
                "missing_f_cnt_ratio": missing_f_cnt_ratio,
                "replica_1_count": replica_distribution["replica_1"],
                "replica_2_count": replica_distribution["replica_2"],
                "replica_3_count": replica_distribution["replica_3"],
                "replica_1_ratio": replica_ratios["replica_1"],
                "replica_2_ratio": replica_ratios["replica_2"],
                "replica_3_ratio": replica_ratios["replica_3"],
            }
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Failed calculate_total_pkt_loss_info: {str(e)}")
            raise ProcessError(f"Error calculate_total_pkt_loss_info: {repr(e)}") from e

    def calculate_mean_variance_distribution_for_rx_pkt(
            self,
            device_id: str,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        try:
            packets = self.get_all_data_for_device_in_gateway(device_id, gateway_id, processed_till_time,
                                                              interval_end_time)

            # Calculate mean and variance for SNR and RSSI
            snr_mean = np.mean([packet.snr for packet in packets if packet.snr is not None])
            rssi_mean = np.mean([packet.rssi for packet in packets if packet.rssi is not None])
            snr_var = np.var([packet.snr for packet in packets if packet.snr is not None])
            rssi_var = np.var([packet.rssi for packet in packets if packet.rssi is not None])

            # Calculate mean and variance for payload size and consumed airtime
            payload_size_mean = np.mean(
                [packet.payload_size for packet in packets if packet.payload_size is not None]
            )
            payload_size_var = np.var(
                [packet.payload_size for packet in packets if packet.payload_size is not None]
            )
            consumed_airtime_mean = np.mean(
                [
                    float(packet.consumed_airtime)
                    for packet in packets
                    if packet.consumed_airtime is not None
                ]
            )
            consumed_airtime_var = np.var(
                [
                    float(packet.consumed_airtime)
                    for packet in packets
                    if packet.consumed_airtime is not None
                ]
            )

            # Calculate the distribution of spreading factors
            spreading_factor_values = [
                int(packet.spreading_factor)
                for packet in packets
                if int(packet.spreading_factor) in range(7, 13)
            ]

            spreading_factor_distribution = {
                str(sf): spreading_factor_values.count(sf) for sf in range(7, 13)
            }

            total_spreading_factor = sum(spreading_factor_distribution.values())

            spreading_factor_ratios = {
                str(sf): count / total_spreading_factor
                for sf, count in spreading_factor_distribution.items()
            }

            # Calculate the distribution of frequencies
            region_freq_list = get_region_freq_plan(packets[0].frequency)

            frequency_distribution = {
                str(freq): sum(1 for packet in packets if str(packet.frequency) == freq)
                for freq in region_freq_list
            }

            total_packets = sum(frequency_distribution.values())

            frequency_ratios = {
                str(freq): count / total_packets for freq, count in frequency_distribution.items()
            }

            return {
                "snr_mean": snr_mean,
                "rssi_mean": rssi_mean,
                "snr_var": snr_var,
                "rssi_var": rssi_var,
                "spreading_factor_distribution": spreading_factor_distribution,
                "spreading_factor_ratios": spreading_factor_ratios,
                "frequency_distribution": frequency_distribution,
                "frequency_ratios": frequency_ratios,
                "payload_size_mean": payload_size_mean,
                "payload_size_var": payload_size_var,
                "consumed_airtime_mean": consumed_airtime_mean,
                "consumed_airtime_var": consumed_airtime_var,
            }
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"Failed calculate_mean_variance_distribution_for_rx_pkt: {str(e)}")
            raise ProcessError(f"Error calculate_mean_variance_distribution_for_rx_pkt: {repr(e)}") from e

    def calculate_consumed_duty_cycle(
            self, device_id: str, processed_till_time: datetime, interval_end_time: datetime
    ):
        try:
            with Session(self.db_engine) as session:
                query = (
                    select(NodeMetadataUl.f_cnt, func.min(NodeMetadataUl.consumed_airtime))
                    .where(
                        NodeMetadataUl.device_id == device_id,
                        NodeMetadataUl.received_at_gw >= processed_till_time,
                        NodeMetadataUl.received_at_gw < interval_end_time,
                    )
                    .group_by(NodeMetadataUl.f_cnt)
                    .order_by(NodeMetadataUl.f_cnt)
                )
                data_rows = session.exec(query).all()
                total_airtime = sum(float(row[1]) for row in data_rows)
                return total_airtime * self.num_tx_replica
        except Exception as e:
            self.logger.error(f"Error in calculate_consumed_duty_cycle: {str(e)}")
            raise DatabaseError("calculate_consumed_duty_cycle ",
                                f"Error in calculate_consumed_duty_cycle: {str(e)}")

    def end_device_kpi_calculation_cycle(
            self, device_id, gateway_id, processed_till_time, interval_end_time
    ):
        try:

            sampling_rate = self.calculate_sampling_rate(
                device_id, processed_till_time, interval_end_time
            )
            self.logger.debug(f"sampling_rate{sampling_rate}")
            # If sampling rate is None, return None
            if sampling_rate is None:
                return None

            # Calculate total uplink packet count and total unique uplink packet count
            total_ul_count = self.get_total_uplink_messages(
                device_id, gateway_id, processed_till_time, interval_end_time
            )
            self.logger.debug(f"total_ul_count{total_ul_count}")
            if not total_ul_count:
                return None
            total_unique_ul_count = self.get_total_unique_uplink_messages(
                device_id, gateway_id, processed_till_time, interval_end_time
            )
            self.logger.debug(f"total_unique_ul_count{total_unique_ul_count}")
            # Calculate packet loss information
            pkt_loss_info = self.calculate_total_pkt_loss_info(
                device_id, processed_till_time, interval_end_time
            )
            self.logger.debug(f"pkt_loss_info{pkt_loss_info}")
            # Calculate packet loss information for a gateway
            pkt_loss_info_gw = self.calculate_total_pkt_loss_info_for_gateway(
                device_id, gateway_id, processed_till_time, interval_end_time
            )
            self.logger.debug(f"pkt_loss_info_gw{pkt_loss_info_gw}")
            # Calculate mean variance and distribution information
            mvd_info = self.calculate_mean_variance_distribution_for_rx_pkt(
                device_id, gateway_id, processed_till_time, interval_end_time
            )
            self.logger.debug(f"mvd_info{mvd_info}")
            # Calculate consumed duty cycle
            consumed_duty_cycle = self.calculate_consumed_duty_cycle(
                device_id, processed_till_time, interval_end_time
            )
            # Construct and return a dictionary containing the KPIs
            return {
                "interval_start_time": processed_till_time,
                "interval_end_time": interval_end_time,
                "device_id": device_id,
                "gateway_id": gateway_id,
                "sampling_rate": sampling_rate,
                "total_dl_pkt_count": 0,
                "total_ul_pkt_count": total_ul_count,
                "total_unique_ul_count": total_unique_ul_count,
                "total_packet_loss": pkt_loss_info["total_packet_loss"],
                "total_packet_loss_ratio": pkt_loss_info["total_packet_loss_ratio"],
                "missing_f_cnt_count": pkt_loss_info["missing_f_cnt_count"],
                "missing_f_cnt_ratio": pkt_loss_info["missing_f_cnt_ratio"],
                "replica_1_count": pkt_loss_info["replica_1_count"],
                "replica_2_count": pkt_loss_info["replica_2_count"],
                "replica_3_count": pkt_loss_info["replica_3_count"],
                "replica_1_ratio": pkt_loss_info["replica_1_ratio"],
                "replica_2_ratio": pkt_loss_info["replica_2_ratio"],
                "replica_3_ratio": pkt_loss_info["replica_3_ratio"],
                "gw_total_packet_loss": pkt_loss_info_gw["gw_total_packet_loss"],
                "gw_total_packet_loss_ratio": pkt_loss_info_gw["gw_total_packet_loss_ratio"],
                "gw_missing_f_cnt_count": pkt_loss_info_gw["gw_missing_f_cnt_count"],
                "gw_missing_f_cnt_ratio": pkt_loss_info_gw["gw_missing_f_cnt_ratio"],
                "gw_replica_1_count": pkt_loss_info_gw["gw_replica_1_count"],
                "gw_replica_2_count": pkt_loss_info_gw["gw_replica_2_count"],
                "gw_replica_3_count": pkt_loss_info_gw["gw_replica_3_count"],
                "gw_replica_1_ratio": pkt_loss_info_gw["gw_replica_1_ratio"],
                "gw_replica_2_ratio": pkt_loss_info_gw["gw_replica_2_ratio"],
                "gw_replica_3_ratio": pkt_loss_info_gw["gw_replica_3_ratio"],
                "consumed_duty_cycle": consumed_duty_cycle,
                "snr_mean": mvd_info["snr_mean"],
                "rssi_mean": mvd_info["rssi_mean"],
                "payload_size_mean": mvd_info["payload_size_mean"],
                "toa_mean": mvd_info["consumed_airtime_mean"],
                "snr_variance": mvd_info["snr_var"],
                "rssi_variance": mvd_info["rssi_var"],
                "payload_size_variance": mvd_info["payload_size_var"],
                "toa_variance": mvd_info["consumed_airtime_var"],
                "spreading_factor_distribution": str(mvd_info["spreading_factor_distribution"]),
                "spreading_factor_ratios": str(mvd_info["spreading_factor_ratios"]),
                "frequency_distribution": str(mvd_info["frequency_distribution"]),
                "frequency_ratios": str(mvd_info["frequency_ratios"]),
            }
        except DatabaseError:
            raise
        except ProcessError:
            raise
        except Exception as e:
            self.logger.error(f"Error in end_device_kpi_calculation_cycle: {str(e)}")
            raise DatabaseError("end_device_kpi_calculation_cycle ",
                                f"Error in end_device_kpi_calculation_cycle: {str(e)}")


class GatewayKPICalculation:
    def __init__(
            self,
            end_device_kpi_calculation: EndDeviceKPICalculation,
            interval_time,
            engine,
            logger,
    ):
        self.db_engine = engine
        self.logger = logger
        self.end_device_kpi_calculation = end_device_kpi_calculation
        self.interval_time = interval_time
        self.processed_till_time = "2023-03-27 00:00:00.000000"

    def store_data(self, data) -> None:
        self.logger.debug(f"store_data")
        """
        Stores the given data object in the database by adding it to the session and committing the transaction.

        Args:
            data: The data object to be stored.

        Returns:
            None
        """
        # self.logger.debug(f"store_data - data: {data}")
        with Session(self.db_engine) as session:
            try:
                session.add(data)
                session.commit()
            except Exception as e:
                self.logger.error(f"Error storing data in the database: {str(e)}")
                session.rollback()

    def get_total_uplink_messages_for_gateway(
            self,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ) -> int:
        self.logger.debug(f"get_total_uplink_messages_for_gateway")
        with Session(self.db_engine) as session:
            query = select(NodeMetadataUl).where(
                NodeMetadataUl.gateway_id == gateway_id,
                NodeMetadataUl.received_at_gw >= processed_till_time,
                NodeMetadataUl.received_at_gw < interval_end_time,
            )
            result = session.exec(query).all()
            return len(result)

    def update_end_devices_ids_none_values(self):
        with Session(self.db_engine) as session:
            # Get all rows from AllRelation table
            all_relations_rows = session.exec(select(AllRelation)).all()

            # Update missing device_id values in TableC
            if all_relations_rows:
                for relation in all_relations_rows:
                    device_id = relation.device_id
                    dev_addr = relation.dev_addr
                    gateway_id = relation.gateway_tti_id

                    rows_to_update = session.exec(
                        select(NodeMetadataUl).where(
                            NodeMetadataUl.device_id is None,
                            NodeMetadataUl.dev_addr == dev_addr,
                            NodeMetadataUl.gateway_id == gateway_id,
                        )
                    ).all()

                    for row in rows_to_update:
                        row.device_id = device_id
                        session.add(row)

                session.commit()

    def sum_all_devices_kpis(self, devices_kpis: List[Dict]) -> Dict:
        num_devices = len(devices_kpis)
        if num_devices:
            try:
                return {
                    "avg_sampling_rate": sum(d["sampling_rate"] for d in devices_kpis)
                                         / num_devices,
                    "total_dl_pkt_count": sum(d["total_dl_pkt_count"] for d in devices_kpis),
                    "total_registered_ul_pkt_count": sum(
                        d["total_ul_pkt_count"] for d in devices_kpis
                    ),
                    "total_unique_ul_count": sum(d["total_unique_ul_count"] for d in devices_kpis),
                    "total_packet_loss": sum(d["total_packet_loss"] for d in devices_kpis),
                    "total_packet_loss_ratio": sum(
                        d["total_packet_loss_ratio"] for d in devices_kpis
                    )
                                               / num_devices,
                    "missing_f_cnt_count": sum(d["missing_f_cnt_count"] for d in devices_kpis),
                    "missing_f_cnt_ratio": sum(d["missing_f_cnt_ratio"] for d in devices_kpis)
                                           / num_devices,
                    "replica_1_count": sum(d["replica_1_count"] for d in devices_kpis),
                    "replica_2_count": sum(d["replica_2_count"] for d in devices_kpis),
                    "replica_3_count": sum(d["replica_3_count"] for d in devices_kpis),
                    "replica_1_ratio": sum(d["replica_1_ratio"] for d in devices_kpis)
                                       / num_devices,
                    "replica_2_ratio": sum(d["replica_2_ratio"] for d in devices_kpis)
                                       / num_devices,
                    "replica_3_ratio": sum(d["replica_3_ratio"] for d in devices_kpis)
                                       / num_devices,
                    "snr_mean": sum(d["snr_mean"] for d in devices_kpis) / num_devices,
                    "rssi_mean": sum(d["rssi_mean"] for d in devices_kpis) / num_devices,
                    "payload_size_mean": sum(d["payload_size_mean"] for d in devices_kpis)
                                         / num_devices,
                    "toa_mean": sum(d["toa_mean"] for d in devices_kpis) / num_devices,
                    "snr_variance": sum(d["snr_variance"] for d in devices_kpis) / num_devices,
                    "rssi_variance": sum(d["rssi_variance"] for d in devices_kpis) / num_devices,
                    "payload_size_variance": sum(d["payload_size_variance"] for d in devices_kpis)
                                             / num_devices,
                    "toa_variance": sum(d["toa_variance"] for d in devices_kpis) / num_devices,
                }
            except Exception as e:
                self.logger.error(f"Error in sum_all_devices_kpis: {str(e)}")

    def get_connected_nodes_info(
            self, gateway_id: str, processed_till_time: datetime, interval_end_time: datetime
    ):
        self.logger.debug(f"get_connected_nodes_info")
        # sourcery skip: collection-builtin-to-comprehension
        with Session(self.db_engine) as session:
            query = (
                select(NodeMetadataUl.dev_addr, NodeMetadataUl.device_id)
                .where(
                    NodeMetadataUl.gateway_id == gateway_id,
                    NodeMetadataUl.received_at_gw >= processed_till_time,
                    NodeMetadataUl.received_at_gw < interval_end_time,
                )
                .distinct()
            )

            result = session.exec(query).all()
            filtered_result = [
                row for row in result if row[0] is not None and row[1] is not None
            ]

            unique_device_ids = set()
            preprocessed_result = []

            for row in filtered_result:
                if row[1] is None:
                    preprocessed_result.append(row)
                elif row[1] not in unique_device_ids:
                    preprocessed_result = [r for r in preprocessed_result if r[1] != row[1]]
                    preprocessed_result.append(row)
                    unique_device_ids.add(row[1])

            num_active_connected_node = len(preprocessed_result)
            num_active_reg_connected_node = len(unique_device_ids)
            num_active_not_reg_connected_node = (
                    num_active_connected_node - num_active_reg_connected_node
            )

            return {
                "num_active_connected_node": num_active_connected_node,
                "num_active_reg_connected_node": num_active_reg_connected_node,
                "num_active_not_reg_connected_node": num_active_not_reg_connected_node,
            }

    def get_gateway_utilization(
            self,
            gateway_id: str,
            processed_till_time: datetime,
            interval_end_time: datetime,
    ):
        self.logger.debug(f"get_gateway_utilization")
        with Session(self.db_engine) as session:
            query = select(NodeMetadataUl.consumed_airtime).where(
                NodeMetadataUl.gateway_id == gateway_id,
                NodeMetadataUl.received_at_gw >= processed_till_time,
                NodeMetadataUl.received_at_gw < interval_end_time,
            )
            consumed_airtime_rows = session.exec(query).all()
            if not consumed_airtime_rows:
                return None
            self.logger.debug(f"total_consumed_airtime{consumed_airtime_rows}")
            self.logger.debug(f"total_consumed_airtime{type(consumed_airtime_rows)}")
            total_consumed_airtime = sum(
                float(consumed_airtime) for consumed_airtime in consumed_airtime_rows
            )

            utilization = (
                    total_consumed_airtime / (interval_end_time - processed_till_time).total_seconds()
            )

            return {
                "total_consumed_airtime": total_consumed_airtime,
                "utilization": utilization,
            }

    def get_jitter_window(
            self, gateway_id: str, processed_till_time: datetime, interval_end_time: datetime
    ):
        self.logger.debug(f"get_jitter_window")
        with Session(self.db_engine) as session:
            # Query for all packets received by the gateway within the specified time period
            query = (
                select(NodeMetadataUl.received_at_gw)
                .where(
                    NodeMetadataUl.gateway_id == gateway_id,
                    NodeMetadataUl.received_at_gw >= processed_till_time,
                    NodeMetadataUl.received_at_gw < interval_end_time,
                )
                .order_by(NodeMetadataUl.received_at_gw)
            )
            results = session.exec(query).all()

            if not results:
                return None

            # Calculate the difference between each successive packet arrival time to get the jitter values
            jitter_values = []
            for i in range(1, len(results)):
                prev_time = results[i - 1]
                curr_time = results[i]
                jitter_values.append((curr_time - prev_time).total_seconds() * 1000)

            # Calculate the average and standard deviation of the jitter values
            num_packets = len(jitter_values)
            avg_jitter = sum(jitter_values) / num_packets if num_packets > 0 else 0
            std_dev_jitter = (
                (sum((x - avg_jitter) ** 2 for x in jitter_values) / num_packets) ** 0.5
                if num_packets > 1
                else 0
            )

            # Return the jitter statistics as a dictionary
            return {"jitter_mean": avg_jitter, "jitter_variance": std_dev_jitter}

    def get_gateway_availability(
            self, gateway_id: str, start_time: datetime, end_time: datetime
    ) -> float:
        self.logger.debug(f"get_gateway_availability")
        with Session(self.db_engine) as session:
            # Step 1: Determine the total time duration of the measurement period.
            start_time = string_to_datetime(str(start_time))
            self.logger.debug(f"end_time type {type(end_time)}{end_time}")
            self.logger.debug(f"start_time type {type(start_time)}{start_time}")
            duration = end_time - start_time
            """ 
                 Step 2: Query the database for the connection status
                 metadata for the gateway during the measurement period. 
            """

            query = (
                select(GatewayConnectionStats)
                .where(
                    GatewayConnectionStats.gateway_id == gateway_id,
                    GatewayConnectionStats.event_time >= start_time,
                    GatewayConnectionStats.event_time < end_time,
                )
                .order_by(GatewayConnectionStats.event_time)
            )
            results = session.exec(query).all()
            """ 
                Step 3: Calculate the total downtime for the gateway by summing 
                the durations of all periods where the 
                gateway was not connected.
            """

            downtime_diff = [
                (next_status.connected_at - status.connected_at)
                for status, next_status in zip(results, results[1:])
                if (next_status.connected_at and status.connected_at) is not None
            ]
            downtime = sum(downtime_diff, timedelta())
            """ 
                Step 4: Calculate the total uptime for the gateway by subtracting 
                the total downtime from the measurement period duration.
            """

            self.logger.debug(f"duration type {type(duration)} {duration}")
            self.logger.debug(f"downtime type {type(downtime)}{downtime}")
            uptime = duration - downtime
            """ 
                Step 5: Calculate the availability as the percentage of
                uptime over the measurement period duration. 
            """

            availability = uptime / duration

            return availability * 100.0

    def calculate_kpis_for_gateway(
            self, gateway_id, all_devices_kpis, processed_till_time, interval_end_time
    ):
        self.logger.debug(f"calculate_kpis_for_gateway")
        all_devices_kpis = self.sum_all_devices_kpis(all_devices_kpis)
        self.logger.debug(f"all_devices_kpis {all_devices_kpis}")
        total_gw_ul_count = self.get_total_uplink_messages_for_gateway(
            gateway_id, processed_till_time, interval_end_time
        )
        self.logger.debug(f"total_gw_ul_count {total_gw_ul_count}")
        connected_nodes_info = self.get_connected_nodes_info(
            gateway_id, processed_till_time, interval_end_time
        )
        self.logger.debug(f"connected_nodes_info {connected_nodes_info}")
        gateway_utilization = self.get_gateway_utilization(
            gateway_id, processed_till_time, interval_end_time
        )
        self.logger.debug(f"gateway_utilization {gateway_utilization}")
        gateway_jitter_window = self.get_jitter_window(
            gateway_id, processed_till_time, interval_end_time
        )
        self.logger.debug(f"gateway_jitter_window {gateway_jitter_window}")
        gateway_availability = self.get_gateway_availability(
            gateway_id, processed_till_time, interval_end_time
        )
        self.logger.debug(f"gateway_availability {gateway_availability}")

        return {
            "interval_start_time": processed_till_time,
            "interval_end_time": interval_end_time,
            "gateway_id": gateway_id,
            "total_ul_pkt_count": total_gw_ul_count,
            "num_active_connected_node": (connected_nodes_info or {}).get(
                "num_active_connected_node"
            ),
            "num_active_reg_connected_node": (connected_nodes_info or {}).get(
                "num_active_reg_connected_node"
            ),
            "num_active_not_reg_connected_node": (connected_nodes_info or {}).get(
                "num_active_not_reg_connected_node"
            ),
            "total_consumed_airtime": (gateway_utilization or {}).get("total_consumed_airtime"),
            "gw_utilization": (gateway_utilization or {}).get("utilization"),
            "jitter_mean": (gateway_jitter_window or {}).get("jitter_mean"),
            "jitter_variance": (gateway_jitter_window or {}).get("jitter_variance"),
            "availability": gateway_availability,
            #   "avg_sampling_rate": (all_devices_kpis or {}).get("avg_sampling_rate"),
            "total_dl_pkt_count": (all_devices_kpis or {}).get("total_dl_pkt_count"),
            "total_registered_ul_pkt_count": (all_devices_kpis or {}).get(
                "total_registered_ul_pkt_count"
            ),
            "total_unique_ul_count": (all_devices_kpis or {}).get("total_unique_ul_count"),
            "total_packet_loss": (all_devices_kpis or {}).get("total_packet_loss"),
            "total_packet_loss_ratio": (all_devices_kpis or {}).get("total_packet_loss_ratio"),
            "missing_f_cnt_count": (all_devices_kpis or {}).get("missing_f_cnt_count"),
            "missing_f_cnt_ratio": (all_devices_kpis or {}).get("missing_f_cnt_ratio"),
            "replica_1_count": (all_devices_kpis or {}).get("replica_1_count"),
            "replica_2_count": (all_devices_kpis or {}).get("replica_2_count"),
            "replica_3_count": (all_devices_kpis or {}).get("replica_3_count"),
            "replica_1_ratio": (all_devices_kpis or {}).get("replica_1_ratio"),
            "replica_2_ratio": (all_devices_kpis or {}).get("replica_2_ratio"),
            "replica_3_ratio": (all_devices_kpis or {}).get("replica_3_ratio"),
            "snr_mean": (all_devices_kpis or {}).get("snr_mean"),
            "rssi_mean": (all_devices_kpis or {}).get("rssi_mean"),
            "payload_size_mean": (all_devices_kpis or {}).get("payload_size_mean"),
            "toa_mean": (all_devices_kpis or {}).get("toa_mean"),
            "snr_variance": (all_devices_kpis or {}).get("snr_variance"),
            "rssi_variance": (all_devices_kpis or {}).get("rssi_variance"),
            "payload_size_variance": (all_devices_kpis or {}).get("payload_size_variance"),
            "toa_variance": (all_devices_kpis or {}).get("toa_variance"),
        }

    def get_all_unique_devices_gateways(self, gateway_id):
        try:
            with Session(self.db_engine) as session:
                query = (
                    select(AllRelation.device_id)
                    .where(AllRelation.gateway_tti_id == gateway_id)
                    .distinct()
                )
                return session.exec(query).all()
        except Exception as e:
            self.logger.error(f"Error in get_all_unique_devices_gateways: {str(e)}")
            raise DatabaseError("get_all_unique_devices_gateways ",
                                f"Error in get_all_unique_devices_gateways: {str(e)}")

    def calculate_end_devices_kpis_for_gateway(
            self, gateway_id: str, processed_till_time, interval_end_time
    ):
        try:
            devices_ids = self.get_all_unique_devices_gateways(gateway_id)
            all_devices_kpis = []
            for device_id in devices_ids:
                self.logger.debug(f"devices_ids :{devices_ids}")
                end_device_kpi = self.end_device_kpi_calculation.end_device_kpi_calculation_cycle(
                    device_id,
                    gateway_id,
                    processed_till_time,
                    interval_end_time,
                )
                self.logger.debug(f"end_device_kpi{end_device_kpi}")
                if end_device_kpi is None:
                    continue
                device_kpi = EndDeviceKPIs(**end_device_kpi)
                all_devices_kpis.append(end_device_kpi)
                self.store_data(device_kpi)
            return all_devices_kpis
        except Exception as e:
            self.logger.error(f"Error in calculate_end_devices_kpis_for_gateway: {repr(e)}")

    def get_all_monitor_gateways(self):
        try:
            with Session(self.db_engine) as session:
                gateways = session.exec(select(MonitoredGateways)).all()
                return [gateway.gateway_id_tti for gateway in gateways]
        except Exception as e:
            self.logger.error(f"Error in get_all_monitor_gateways: {str(e)}")
            raise DatabaseError("get_all_monitor_gateways ",
                                f"Error in get_all_monitor_gateways: {str(e)}")

    def calculate_kpis_for_all_monitor_gateways(self, processed_till_time, interval_end_time):
        try:
            gateways_ids = self.get_all_monitor_gateways()
            for gateways_id in gateways_ids:
                self.logger.debug(f"gateways_ids :{gateways_ids}")
                all_devices_kpis = self.calculate_end_devices_kpis_for_gateway(
                    gateways_id, processed_till_time, interval_end_time
                )
                self.logger.debug(f"all_devices_kpis :{all_devices_kpis}")
                gateway_kpis = self.calculate_kpis_for_gateway(
                    gateways_id, all_devices_kpis, processed_till_time, interval_end_time
                )
                if gateway_kpis is None:
                    continue
                gateway_kpis = GatewayKPIs(**gateway_kpis)
                self.store_data(gateway_kpis)
        except Exception as e:
            self.logger.error(f"Error in calculate_kpis_for_all_monitor_gateways: {repr(e)}")

    def scheduled_func(self):
        self.logger.debug(f"scheduled_func")
        try:
            _, last_arrival_time = self.get_min_max_arrival_time()

            if last_arrival_time is not None:
                processing_time_window = timedelta(minutes=self.interval_time)
                while (last_arrival_time - string_to_datetime(str(self.processed_till_time))) > processing_time_window:
                    interval_end_time = (string_to_datetime(str(self.processed_till_time)) + processing_time_window)
                    self.calculate_kpis_for_all_monitor_gateways(self.processed_till_time, interval_end_time)
                    self.processed_till_time = interval_end_time
                    _, last_arrival_time = self.get_min_max_arrival_time()

            schedule.every(self.interval_time).minutes.do(self.scheduled_func)
        except ValueError as e:
            self.logger.error(f"Error in the scheduled_func due to string_to_datetime conversion: {repr(e)}")

        except Exception as e:
            self.logger.error(f"Error in scheduled_func: {repr(e)}")

    def get_min_max_arrival_time(self):
        try:
            with Session(self.db_engine) as session:
                query = select(
                    func.min(NodeMetadataUl.received_at_gw), func.max(NodeMetadataUl.received_at_gw)
                )
                result = session.exec(query).one_or_none()
                if result is None:
                    return None
                else:
                    return result[0], result[1]
        except Exception as e:
            self.logger.error(f"Error in get_min_max_arrival_time: {str(e)}")
            raise DatabaseError("get_min_max_arrival_time ",
                                f"Error in get_min_max_arrival_time: {str(e)}")

    def gateway_kpis_calculations_cycle(self):
        self.logger.debug(f"gateway_kpis_calculations_cycle")
        try:
            first_arrival_time, _ = self.get_min_max_arrival_time()
            self.processed_till_time = first_arrival_time
            while not first_arrival_time:
                self.logger.debug(f"there is no data in the tables")
                first_arrival_time, _ = self.get_min_max_arrival_time()
                self.processed_till_time = first_arrival_time
                time.sleep(60)

            # Schedule the function to run every interval_time seconds
            self.scheduled_func()

            # Run the scheduled functions indefinitely
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in gateway_kpis_calculations_cycle: {repr(e)}")


def run_kpi_calculations():
    num_tx_replica = 3
    # Set the interval time to one hour
    kpi_calculation_cycle = os.getenv("KPI_CALCULATION_CYCLE")

    # Create a logger
    kpi_logger = utility_functions.get_logger(logger_config)
    kpi_logger.debug(f"run_kpi_calculations start")
    # Create an instance of EndDeviceKPICalculation
    end_device_kpi_calculation = EndDeviceKPICalculation(db_engine, num_tx_replica, kpi_logger)

    # Create an instance of GatewayKPICalculation
    gateway_kpi_calculation = GatewayKPICalculation(
        end_device_kpi_calculation, int(kpi_calculation_cycle), db_engine, kpi_logger
    )
    gateway_kpi_calculation.gateway_kpis_calculations_cycle()
