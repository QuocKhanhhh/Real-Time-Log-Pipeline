from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, count, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

spark = SparkSession.builder \
    .appName("WebLogsAnalysis") \
    .master("spark://spark-master:7077") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

schema = StructType([
    StructField("timestamp", StringType(), True),
    StructField("user_id", StringType(), True),
    StructField("ip_address", StringType(), True),
    StructField("action", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("user_agent", StringType(), True),
    StructField("response_time", FloatType(), True),
    StructField("status_code", IntegerType(), True)
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "web_logs") \
    .load()

logs_df = df.select(from_json(col("value").cast("string"),schema).alias("data")).select("data.*") \
    .withColumn("timestamp", to_timestamp(col("timestamp"))) \
    .withWatermark("timestamp", "10 minutes") 

# Phân tích 1: Số lượt xem sản phẩm theo window 5 phút
product_views = logs_df.filter(col("action") == "view_product") \
    .groupBy(window(col("timestamp"), "5 minutes"),col("product_id")) \
    .agg(count("*").alias("view_count")) \
    .select(col("window.start").alias("window_start"), col("product_id"), col("view_count"))

# Phân tích 2: Tỷ lệ hành động (view_product, add_to_cart, checkout)
action_counts = logs_df.groupBy(window(col("timestamp"), "5 minutes"), col("action")) \
    .agg(count("*").alias("action_count")) \
    .select(col("window.start").alias("window_start"), col("action"), col("action_count"))

# # Phân tích 3: Phát hiện bot (IP có hơn 10 yêu cầu/phút)
# bot_detection = logs_df.groupBy(window(col("timestamp"), "1 minute"), col("ip_address")) \
#     .agg(count("*").alias("request_count")) \
#     .filter(col("request_count") > 10) \
#     .select(col("window.start").alias("window_start"), col("ip_address"), col("request_count"))

# Phân tích 4: Thời gian phản hồi trung bình theo hành động
# response_time_avg = logs_df.groupBy(window(col("timestamp"), "5 minutes"), col("action")) \
    # .agg(expr("avg(response_time)").alias("avg_response_time"))

# Phân tích 4: Phát hiện lỗi thanh toán (status_code 500 cho checkout)
# payment_errors = logs_df.filter((col("action") == "checkout") & (col("status_code") == 500)) \
#     .groupBy(window(col("timestamp"), "5 minutes")) \
#     .agg(count("*").alias("error_count")) \
#     .select(col("window.start").alias("window_start"), col("error_count"))

def write_to_postgres(batch_df, batch_id, table_name):
    batch_df.write \
        .format("jdbc") \
        .option("driver", "org.postgresql.Driver") \
        .option("url", "jdbc:postgresql://postgres:5432/weblogs") \
        .option("dbtable", table_name) \
        .option("user", "admin") \
        .option("password", "admin123") \
        .mode("append") \
        .save()

product_views.writeStream \
    .foreachBatch(lambda df, id: write_to_postgres(df, id, "product_views")) \
    .trigger(processingTime="10 seconds") \
    .start()

action_counts.writeStream \
    .foreachBatch(lambda df, id: write_to_postgres(df, id, "action_counts")) \
    .trigger(processingTime="10 seconds") \
    .start()



# payment_errors.writeStream \
#     .format("csv") \
#     .outputMode("append") \
#     .option("path", "/tmp/output/action_counts") \
#     .option("checkpointLocation", "/tmp/checkpoint/action_counts") \
#     .option("header", "true") \
#     .trigger(processingTime="10 seconds") \
#     .start()

spark.streams.awaitAnyTermination()