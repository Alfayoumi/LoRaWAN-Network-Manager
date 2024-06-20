import concurrent
import concurrent.futures
import json
from typing import Any, Dict, List

import pika
from sqlmodel import Session, select

from dependencies.exceptions import RabbitMQConnectionError, RabbitMQConsumingError, ParsingError, DatabaseError
from dependencies.utility_functions import calculate_toa, get_payload_size
from stream_event_consumer.database.models import (
    AllRelation,
    GatewayConnectionStats,
    GatewayStatusReceive,
    NodeMetadataDl,
    NodeMetadataUl,
    PacketReplicaMetadata,
)

num_tx_replica = 3
threshold_f_cnt = 3


class MessageConsumer:
    def __init__(
            self,
            logger,
            rabbit_username,
            rabbit_password,
            rabbit_host,
            queue_name,
            db_engine,
            max_threads,
    ):
        """
        Initialize a MessageConsumer object with the given parameters.

        Args:
            logger: A logger object for logging events.
            rabbit_username: The username for connecting to the RabbitMQ instance.
            rabbit_password: The password for connecting to the RabbitMQ instance.
            rabbit_host: The hostname for the RabbitMQ instance.
            queue_name: The name of the RabbitMQ queue to consume messages from.
            db_engine: A SQLAlchemy engine object for connecting to a database.
        """
        self.logger = logger
        self.rabbit_username = rabbit_username
        self.rabbit_password = rabbit_password
        self.rabbit_host = rabbit_host
        self.queue_name = queue_name
        self.credentials = pika.PlainCredentials(
            username=self.rabbit_username, password=self.rabbit_password
        )
        self.rx_event_message = {}
        self.db_engine = db_engine
        self.max_threads = max_threads
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads)
        self.logger.debug("initialize - Message logger connector")

    @staticmethod
    def parse_sub_bands(sub_bands):
        try:
            sub_band_info = {}
            for i, sub_band in enumerate(sub_bands):
                sub_band_info[f"min_freq_band_{i}"] = sub_band.get("min_frequency")
                sub_band_info[f"max_freq_band_{i}"] = sub_band.get("max_frequency")
                sub_band_info[f"dl_utilization_limit_band_{i}"] = sub_band.get("downlink_utilization_limit")
                sub_band_info[f"dl_utilization_band_{i}"] = sub_band.get("downlink_utilization")
            return sub_band_info
        except Exception as e:
            raise ParsingError("Error occurred while parsing sub-bands.") from e

    @staticmethod
    def parse_metrics(metrics):
        try:
            return {
                k: metrics.get(k, None)
                for k in ["txin", "txok", "lpps", "rxin", "rxok", "rxfw", "ackr"]
            }
        except Exception as e:
            raise ParsingError("Error occurred while parsing metrics.") from e

    @staticmethod
    def parse_round_trip_times(data):
        try:
            round_trip_times = data.get("round_trip_times", {})
            return {
                "min_round_trip_times": round_trip_times.get("min"),
                "max_round_trip_times": round_trip_times.get("max"),
                "median_round_trip_times": round_trip_times.get("median"),
                "count_round_trip_times": round_trip_times.get("count"),
            }
        except Exception as e:
            raise ParsingError("Error occurred while parsing round-trip times.") from e

    @staticmethod
    def get_common_features(rx_event_message) -> Dict[str, Any]:
        try:
            result = rx_event_message["result"]
            identifiers = result.get("identifiers", [{}])[0].get("gateway_ids", {})
            return {
                "name": result.get("name"),
                "time": result.get("time"),
                "gateway_id": identifiers.get("gateway_id"),
                "gateway_eui": identifiers.get("eui"),
                "tenant-id": result.get("context", {}).get("tenant-id"),
                "rights": result.get("visibility", {}).get("rights", [])[0],
                "unique_id": result.get("unique_id"),
            }
        except Exception as e:
            raise ParsingError("Error occurred while extracting common features.") from e

    def decode_gs_gateway_connection_stats(self, rx_event_message):
        """
        Parses the gateway connection stats information of a gateway and
        returns a dictionary containing relevant data.

        Args:
            rx_event_message: A dictionary containing the gateway connection stats information.
        """
        try:
            common_features = self.get_common_features(rx_event_message)
            data = rx_event_message.get("result", {}).get("data")
            if data is None:
                return None

            last_status = data.get("last_status", {})
            versions = last_status.get("versions", {})
            metrics = self.parse_metrics(last_status.get("metrics", {}))
            if metrics is None:
                metrics = {}
            round_trip_times = self.parse_round_trip_times(data)
            sub_bands = self.parse_sub_bands(data.get("sub_bands", {}))
            if sub_bands is None:
                sub_bands = {}
            antenna_locations = last_status.get("antenna_locations", [{}])[0]

            return {
                "event_name": common_features.get("name"),
                "event_time": common_features.get("time"),
                "gateway_id": common_features.get("gateway_id"),
                "gateway_eui": common_features.get("gateway_eui"),
                "connected_at": data.get("connected_at"),
                "protocol": data.get("protocol"),
                "last_status_received_at": data.get("last_status_received_at"),
                "last_status_time": last_status.get("time"),
                "last_uplink_received_at": data.get("last_uplink_received_at"),
                "last_downlink_received_at": data.get("last_downlink_received_at"),
                "boot_time": last_status.get("boot_time"),
                "ttn_lw_gateway_server": versions.get("ttn-lw-gateway-server"),
                "fpga": versions.get("fpga"),
                "hal": versions.get("hal"),
                "latitude": antenna_locations.get("latitude"),
                "longitude": antenna_locations.get("longitude"),
                "altitude": antenna_locations.get("altitude"),
                "source": antenna_locations.get("source"),
                "ip": last_status.get("ip", [None])[0],
                **metrics,
                **round_trip_times,
                **sub_bands,
                "uplink_count": data.get("uplink_count"),
                "downlink_count": data.get("downlink_count"),
            }
        except ParsingError as e:
            self.logger.error(f"Error occurred while decoding gs_gateway_connection_stats: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Error occurred while decoding gs_gateway_connection_stats: {str(e)}")
            raise ParsingError("Error occurred while decoding gs_gateway_connection_stats.") from e

    def parse_gs_up_message(self, message) -> dict:
        try:
            parsed_message = {
                "raw_payload": None,
                "frm_payload": None,
                "f_ctrl_adr": None,
                "f_cnt": None,
                "dev_addr": None,
                "f_port": None,
                "join_eui": None,
                "dev_eui": None,
                "dev_nonce": None,
            }

            mac_payload = message.get("payload", {}).get("mac_payload", {})
            parsed_message["raw_payload"] = message.get("raw_payload", {})
            if "f_hdr" in mac_payload:
                f_hdr = mac_payload["f_hdr"]
                parsed_message["f_ctrl_adr"] = f_hdr["f_ctrl"].get("adr")
                parsed_message["f_cnt"] = f_hdr.get("f_cnt")
                parsed_message["dev_addr"] = f_hdr.get("dev_addr")
                parsed_message["f_port"] = mac_payload.get("f_port")
                parsed_message["frm_payload"] = mac_payload.get("frm_payload")

            join_payload = message.get("payload", {}).get("join_request_payload", {})
            if join_payload:
                parsed_message["join_eui"] = join_payload.get("join_eui")
                parsed_message["dev_eui"] = join_payload.get("dev_eui")
                parsed_message["dev_nonce"] = join_payload.get("dev_nonce")

            return parsed_message

        except Exception as e:
            self.logger.error(f"Error occurred while parsing gs_up_message: {str(e)}")
            raise ParsingError("Failed to parse gateway uplink message in parse_gs_up_message function") from e

    def decode_gs_down_send(self, rx_event_message):
        try:
            common_features = self.get_common_features(rx_event_message)
            data = rx_event_message.get("result", {}).get("data", {})
            scheduled = data.get("scheduled", {})

            data_rate = scheduled.get("data_rate", {}).get("lora", {})
            downlink = scheduled.get("downlink", {})

            return {
                "event_time": common_features.get("time"),
                "gateway_id": common_features.get("gateway_id"),
                "gateway_eui": common_features.get("gateway_eui"),
                "raw_payload": data.get("raw_payload"),
                "bandwidth": data_rate.get("bandwidth"),
                "spreading_factor": data_rate.get("spreading_factor"),
                "coding_rate": data_rate.get("coding_rate"),
                "frequency": scheduled.get("frequency"),
                "timestamp": scheduled.get("timestamp"),
                "concentrator_timestamp": scheduled.get("concentrator_timestamp"),
                "tx_power": float(downlink.get("tx_power")),
                "invert_polarization": downlink.get("invert_polarization"),
            }
        except Exception as e:
            self.logger.error(f"Error occurred while decoding gs.down.send message: {str(e)}")
            raise ParsingError(f"Failed to decode gs.down.send message.{repr(e)}") from e

    def decode_gs_status_receive(self, rx_event_message):
        try:
            common_features = self.get_common_features(rx_event_message)
            result_data = rx_event_message.get("result", {}).get("data", {})
            versions = result_data.get("versions", {})
            antenna_location = result_data.get("antenna_locations", [{}])[0]
            metrics = result_data.get("metrics", {})

            return {
                "name": common_features.get("name"),
                "event_time": common_features.get("time"),
                "gateway_id": common_features.get("gateway_id"),
                "gateway_eui": common_features.get("gateway_eui"),
                "time": result_data.get("time"),
                "boot_time": result_data.get("boot_time"),
                "ttn_lw_gateway_server": versions.get("ttn-lw-gateway-server"),
                "fpga": versions.get("fpga"),
                "hal": versions.get("hal"),
                "latitude": antenna_location.get("latitude", None),
                "longitude": antenna_location.get("longitude", None),
                "altitude": antenna_location.get("altitude", None),
                "source": antenna_location.get("source", None),
                "ip": result_data.get("ip", [None])[0],
                "txin": metrics.get("txin", None),
                "txok": metrics.get("txok", None),
                "lpps": metrics.get("lpps", None),
                "rxin": metrics.get("rxin", None),
                "rxok": metrics.get("rxok", None),
                "rxfw": metrics.get("rxfw", None),
                "ackr": metrics.get("ackr", None),
            }
        except Exception as e:
            self.logger.error(f"Error occurred while decoding gs.status.receive message: {str(e)}")
            raise ParsingError(f"Failed to decode gs.status.receive message.{repr(e)}")

    def store_data(self, data) -> None:
        """
        Stores the given data object in the database by adding it to the session and committing the transaction.

        Args:
            data: The data object to be stored.
        """
        with Session(self.db_engine) as session:
            try:
                session.add(data)
                session.commit()
                self.logger.debug("Data stored successfully in the database.")
            except Exception as e:
                self.logger.error(f"Error storing data in the database: {str(e)}")
                raise DatabaseError("store_data ", f"Error storing data in the database: {str(e)}")
            finally:
                session.close()

    def get_all_packet_replica(self, dev_addr, gateway_id, f_cnt) -> List[PacketReplicaMetadata]:
        """
        Returns all packet replicas from the database for a given device address and frame counter.
        """
        try:
            with Session(self.db_engine) as session:
                statement = select(PacketReplicaMetadata).where(
                    PacketReplicaMetadata.dev_addr == dev_addr,
                    PacketReplicaMetadata.gateway_id == gateway_id,
                    PacketReplicaMetadata.f_cnt == f_cnt,
                )
                return session.exec(statement).all()
        except Exception as e:
            self.logger.error(f"get_all_packet_replica, Error getting packet replicas from the database: {str(e)}")
            raise DatabaseError("get_all_packet_replica ",
                                f"Error getting packet replicas from the database: {str(e)}")
        finally:
            session.close()

    def get_packet_data(self, dev_addr: str, gateway_id: str, received_at_gw: str):
        """
        Returns the packet replica from the database for a given device address, gateway ID, and received time.

        Args:
            dev_addr: The device address.
            gateway_id: The ID of the gateway that received the packet.
            received_at_gw: The time the packet was received by the gateway.

        Returns:
            A PacketReplicaMetadata object from the database if found, None otherwise.
        """
        with Session(self.db_engine) as session:
            try:
                statement = (
                    select(PacketReplicaMetadata)
                    .where(PacketReplicaMetadata.dev_addr == dev_addr)
                    .where(PacketReplicaMetadata.gateway_id == gateway_id)
                    .where(PacketReplicaMetadata.received_at_gw == received_at_gw)
                )
                result = session.exec(statement).first()
                if result is None:
                    self.logger.warning(
                        f"No packet replica found for dev_addr: {dev_addr}, gateway_id: {gateway_id}, received_at_gw: {received_at_gw}")
                return result
            except Exception as e:
                self.logger.error(f"Error getting packet replica from the database: {str(e)}")
                return None

    def update_packet_replica_metadata(self, dev_addr, gateway_id, f_cnt):
        try:
            self.logger.debug(f" update_packet_replica_metadata ")
            with Session(self.db_engine) as session:
                all_replica = self.get_all_packet_replica(dev_addr, gateway_id, f_cnt)
                self.logger.debug(f" all_replica : {all_replica} ")
                tot_rx_replica = len(list(all_replica))
                gw_list = [packet_rx_replica.gateway_id for packet_rx_replica in all_replica]
                num_gws = len(set(gw_list))
                count_list = [gw_list.count(gw) for gw in set(gw_list)]
                num_rx_replica = max(count_list)
                self.logger.debug(f" tot_rx_replica{tot_rx_replica} ")
                for packet_rx_replica in all_replica:
                    packet_rx_replica.num_rx_replica = num_rx_replica
                    packet_rx_replica.num_loss_replica = max((num_tx_replica - num_rx_replica), 0)
                    packet_rx_replica.num_gws = num_gws
                    packet_rx_replica.tot_rx_replica = tot_rx_replica
                    packet_rx_replica.tot_loss_replica = max(
                        ((num_gws * num_tx_replica) - tot_rx_replica), 0
                    )
                    session.add(packet_rx_replica)
                    session.commit()
        except DatabaseError:
            raise
        except Exception as e:
            self.logger.error(f"update_packet_replica_metadata, Error update_packet_replica_metadata: {str(e)}")
            raise DatabaseError("update_packet_replica_metadata ",
                                f"Error update_packet_replica_metadata: {str(e)}")
        finally:
            session.close()

    def store_new_packet_replica_metadata(self, pkt_data):
        """
        Stores new packet replica metadata in the database.

        Args:
            pkt_data: A dictionary containing the packet replica metadata to be stored.

        Returns:
            None.
        """
        try:
            self.logger.debug(f" store_new_packet_replica_metadata ")
            new_packet = {
                "device_id": pkt_data.get("device_id", None),
                "dev_addr": pkt_data.get("dev_addr", None),
                "gateway_id": pkt_data.get("gateway_id", None),
                "f_cnt": pkt_data.get("f_cnt", None),
                "received_at_gw": pkt_data.get("received_at_gw", None),
            }
            self.store_data(PacketReplicaMetadata(**new_packet))
        except DatabaseError:
            self.logger.error(f"Error store_new_packet_replica_metadata  data in the database")
            raise
        except Exception as e:
            self.logger.error(f"Error store_new_packet_replica_metadata in the database: {repr(e)} ")
            raise DatabaseError("store_new_packet_replica_metadata ",
                                f"Error store_new_packet_replica_metadata: {repr(e)}")

    def calculate_pkt_replica_number(self, pkt_data) -> None:
        """
        Calculates the packet replica number for a given packet.

        Args:
            pkt_data: A dictionary containing packet data.

        Returns:
            None.
        """
        try:
            self.logger.debug(f"calculate_pkt_replica_number")
            dev_addr = pkt_data["dev_addr"]
            gateway_id = pkt_data["gateway_id"]
            f_cnt = pkt_data["f_cnt"]
            received_at_gw = pkt_data["received_at_gw"]

            packet_data = self.get_packet_data(dev_addr, gateway_id, received_at_gw)
            if packet_data is None:
                self.store_new_packet_replica_metadata(pkt_data)
                self.update_packet_replica_metadata(dev_addr, gateway_id, f_cnt)

        except DatabaseError:
            self.logger.error(f"Error calculate_pkt_replica_number  data in the database")
            raise
        except Exception as e:
            self.logger.error(f"Error calculate_pkt_replica_number: {repr(e)}")
            raise DatabaseError("calculate_pkt_replica_number ",
                                f"Error calculate_pkt_replica_number: {repr(e)}")

    def get_device_id_by_dev_addr_and_gateway_tti_id(self, dev_addr, last_f_cnt, gateway_tti_id):
        self.logger.debug("get_device_id_by_dev_addr_and_gateway_tti_id")
        with Session(self.db_engine) as session:
            statement = select(AllRelation).where(
                AllRelation.dev_addr == dev_addr,
                AllRelation.gateway_tti_id == gateway_tti_id,
            )
            result = session.exec(statement).all()

            if result:
                closest_device_id = None
                min_f_cnt_diff = float('inf')

                for metadata in result:
                    f_cnt_diff = abs(int(metadata.last_f_cnt) - int(last_f_cnt))

                    if f_cnt_diff < min_f_cnt_diff:
                        min_f_cnt_diff = f_cnt_diff
                        closest_device_id = metadata.device_id

                return closest_device_id

        return None

    def decode_gs_up_receive(self, rx_event_message) -> Dict[str, Any]:
        """
        Decodes a gateway uplink message and returns a dictionary containing relevant data.

        Args:
            rx_event_message: The received event message.
        """
        try:
            common_features = self.get_common_features(rx_event_message)
            message = rx_event_message["result"]["data"].get("message", {})
            settings = message.get("settings", {})
            m_type = message.get("payload", {}).get("m_hdr", {}).get("m_type")
            rx_metadata = message.get("rx_metadata", {})

            channel_index = rx_metadata[0].get("channel_index")
            snr = rx_metadata[0].get("snr")
            gps_time = rx_metadata[0].get("gps_time")

            parsed_message = self.parse_gs_up_message(message)

            device_id = self.get_device_id_by_dev_addr_and_gateway_tti_id(
                parsed_message.get("dev_addr"), parsed_message.get("f_cnt"), common_features.get("gateway_id"))
            spreading_factor = settings.get("data_rate", {}).get("lora", {}).get("spreading_factor")
            payload_size = get_payload_size(parsed_message.get("raw_payload"))
            consumed_airtime = calculate_toa(payload_size, spreading_factor)["t_packet"]
            return {
                "event_time": str(common_features.get("time")),
                "gateway_id": common_features.get("gateway_id"),
                "gateway_eui": common_features.get("gateway_eui"),
                "raw_payload": message.get("raw_payload"),
                "m_type": m_type,
                "dev_addr": parsed_message.get("dev_addr"),
                "device_id": device_id,
                "f_ctrl_adr": parsed_message.get("f_ctrl_adr"),
                "f_port": parsed_message.get("f_port"),
                "f_cnt": parsed_message.get("f_cnt"),
                "join_eui": parsed_message.get("join_eui"),
                "dev_eui": parsed_message.get("dev_eui"),
                "dev_nonce": parsed_message.get("dev_nonce"),
                "frm_payload": parsed_message.get("frm_payload"),
                "bandwidth": settings.get("data_rate", {}).get("lora", {}).get("bandwidth"),
                "spreading_factor": spreading_factor,
                "coding_rate": settings.get("data_rate", {}).get("lora", {}).get("coding_rate"),
                "frequency": settings.get("frequency"),
                "consumed_airtime": consumed_airtime,
                "payload_size": payload_size,
                "timestamp": settings.get("timestamp"),
                "time": str(settings.get("time")),
                "rssi": rx_metadata[0].get("rssi"),
                "channel_rssi": rx_metadata[0].get("channel_rssi"),
                "snr": snr,
                "channel_index": channel_index,
                "gps_time": gps_time,
                "received_at_gw": rx_metadata[0].get("received_at"),
                "received_at_tti": message.get("received_at"),
            }
        except Exception as e:
            self.logger.error(f"Error decode_gs_up_receive: {repr(e)}")

    def decode_rx_message(self, event_name, rx_event_message):
        try:
            if event_name == "gs.up.receive":
                decoded_message_json = self.decode_gs_up_receive(rx_event_message)
                metadata = NodeMetadataUl(**decoded_message_json)
                self.store_data(metadata)
                self.calculate_pkt_replica_number(decoded_message_json)

            elif event_name == "gs.down.send":
                decoded_message_json = self.decode_gs_down_send(rx_event_message)
                metadata = NodeMetadataDl(**decoded_message_json)
                self.store_data(metadata)

            elif event_name == "gs.status.receive":
                decoded_message_json = self.decode_gs_status_receive(rx_event_message)
                metadata = GatewayStatusReceive(**decoded_message_json)
                self.store_data(metadata)

            elif event_name == "gs.gateway.connection.stats":
                decoded_message_json = self.decode_gs_gateway_connection_stats(rx_event_message)
                metadata = GatewayConnectionStats(**decoded_message_json)
                self.store_data(metadata)

            else:
                self.logger.debug(f"event not process")

        except Exception as e:
            self.logger.error(f"Error decode_rx_message: {repr(e)}")

    def consume(self, event_message):
        if len(event_message) > 100:
            try:
                rx_event_message = json.loads(event_message)
                rx_event_message = json.loads(rx_event_message)
                event_name = rx_event_message["result"]["name"]
                self.logger.debug(f"event_name =  {event_name}")
                self.decode_rx_message(event_name, rx_event_message)

            except Exception as e:
                self.logger.error(f"ERROR in the consuming: {repr(e)}")

    def callback(self, ch, method, properties, body):
        try:
            self.thread_pool.submit(self.consume, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            self.logger.error(f"Error in callback function: {repr(e)}")
            raise

    def start_consuming(self):
        self.logger.debug(f"start stream event consumer service ")
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbit_host, credentials=self.credentials)
            )
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)
        except Exception as e:
            self.logger.error(f"Failed to connect to RabbitMQ: {repr(e)}")
            raise RabbitMQConnectionError("Failed to connect to RabbitMQ.") from e

        try:
            for _ in range(self.max_threads):
                channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback)
            channel.start_consuming()
        except Exception as e:
            self.logger.error(f"RabbitMQ channel was closed: {repr(e)}")
            raise RabbitMQConsumingError(f"Error starting RabbitMQ consumer: {repr(e)}") from e
