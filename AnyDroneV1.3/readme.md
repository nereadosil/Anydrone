Steps to run the web server:
-Install DB browser for sqlite in order to check data is loading properly into the database.
-Run this command to run the web server: python app.py 
-Go to this address http://127.0.0.1:5000
-Once you are into the web page try to register a user and login with it. Check that it is stored into the database.
-Once you login you can try to add a drone and check that it is being stored into the database too. 





Add drones to database with different coordinates.
-- Madrid, Spain
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'SkyView M1', 'AeroTech', '4K', 2.5, 30, 40.4168, -3.7038);

-- Paris, France
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'Flyer Pro', 'DroneCorp', '1080p', 1.8, 25, 48.8566, 2.3522);

-- New York City, USA
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'EagleEye X', 'SkyLab', '4K HDR', 3.0, 35, 40.7128, -74.0060);

-- Tokyo, Japan
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'Nimbus 300', 'FutureFly', '2.7K', 1.5, 28, 35.6895, 139.6917);

-- Berlin, Germany
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'FalconEye', 'RotorOne', '1080p', 2.0, 32, 52.5200, 13.4050);

-- Buenos Aires, Argentina
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'SouthView X', 'DroneSouth', '4K', 2.2, 30, -34.6037, -58.3816);

-- Nairobi, Kenya
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'Savannah Scout', 'AirTrack', 'HD', 1.0, 20, -1.2921, 36.8219);

-- Sydney, Australia
INSERT INTO drones (owner_id, model, manufacturer, camera_quality, max_load, flight_time, latitude, longitude)
VALUES (1, 'Outback Flyer', 'AussieDrones', '4K', 2.3, 33, -33.8688, 151.2093);
