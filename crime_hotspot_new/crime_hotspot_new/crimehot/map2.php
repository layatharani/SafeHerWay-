<?php
include("dbconnect.php");
extract($_REQUEST);
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
<title>Untitled Document</title>
 <script type="text/javascript"
      src="http://maps.google.com/maps/api/js?sensor=false&key=AIzaSyAzfJHU7mKkVKW9nTVPymNY-0emhlP-0DQ&v=3.21.5a&libraries=drawing&signed_in=true&libraries=places,drawing"></script>
</head>

<body>
<?php
$data=array();
$latt="";
$lonn="";

$i=0;

$qq=mysqli_query($connect,"SELECT * FROM ch_location where district='$district'");
$rr=mysqli_fetch_array($qq);
$latt=$rr['lat'];
$lonn=$rr['lon'];
   
$q1=mysqli_query($connect,"SELECT * FROM ch_location where district='$district'");
   while($r1=mysqli_fetch_array($q1))
{
   
    #df=pd.read_csv('static/dataset/crime_area.csv')

    $dt=array();
       $dt[]=$r1['area'];
       $dt[]=$r1['lat'];
       $dt[]=$r1['lon'];
       $dt[]=$r1['district'];
       $dt[]=$r1['pincode'];
       $dt[]=$r1['crime'];
     $data[$i]=$dt;
	 $i++;  
	}
	


?>

  <div id="map" style="height: 800px; width: 800px;">
</div>
<script type="text/javascript">

    var locations = [
		<?php
		foreach($data as $dd)
		{
		
		?>
		
      ['<?php echo $dd[0].", ".$dd[3].", ".$dd[4]." <br>(".$dd[5].")"; ?>', <?php echo $dd[1]; ?>, <?php echo $dd[2]; ?>, 4],
	  	
		<?php
		}
		?>
      /*['Coogee Beach', -33.923036, 151.259052, 5],
      ['Cronulla Beach', -34.028249, 151.157507, 3],
      ['Manly Beach', -33.80010128657071, 151.28747820854187, 2],
      ['Maroubra Beach', -33.950198, 151.259302, 1]*/
    ];
	
	
	
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 10,
      center: new google.maps.LatLng(<?php echo $latt; ?>, <?php echo $lonn; ?>),
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    var infowindow = new google.maps.InfoWindow();

    var marker, i;

    for (i = 0; i < locations.length; i++) { 
      marker = new google.maps.Marker({
        position: new google.maps.LatLng(locations[i][1], locations[i][2]),
        map: map
      });
//marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');
      google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
          infowindow.setContent(locations[i][0]);
          infowindow.open(map, marker);
        }
      })(marker, i));
    }
	////////
	 for (i = 0; i < locations2.length; i++) { 
      marker = new google.maps.Marker({
        position: new google.maps.LatLng(locations2[i][1], locations2[i][2]),
        map: map
      });
marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');
      google.maps.event.addListener(marker, 'click', (function(marker, i) {
        return function() {
          infowindow.setContent(locations2[i][0]);
          infowindow.open(map, marker);
        }
      })(marker, i));
    }
	
	
//////////////////////////////////////	
	
	
  </script> 

</body>
</html>
