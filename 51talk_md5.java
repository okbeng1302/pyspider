package com.xiaobai.parse;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.Map;
import java.util.SortedMap;
import java.util.TreeMap;

import org.apache.commons.codec.binary.Base64;


import sun.misc.*; 
public class test {
	
	public static void main(String args[]){
		Map map = new HashMap();
		Object obj = new TreeMap();
		((SortedMap) (obj)).put("talk_token", "jj0dYZjvGhkNvG7r1svc8rGuEDd9DD1KfJ1s/q7ItTdsVwJ16PLqJ9fds/PCz4dsVfhIshsNlk9MeropQOWKs/BgPgpTcx0HVPh9x-A=");
        ((SortedMap) (obj)).put("userId", "37160010");
        ((SortedMap) (obj)).put("page", "1");
		((SortedMap) (obj)).put("version", "4.5.2");
        ((SortedMap) (obj)).put("channel", "360zs");
        ((SortedMap) (obj)).put("systemVer", "23");
        ((SortedMap) (obj)).put("deviceId", "355592070880643");
        ((SortedMap) (obj)).put("deviceType", "Nexus 5X");
        ((SortedMap) (obj)).put("phoneType", "andr");
        
        obj = generateTsignValue(((SortedMap) (obj)));
        map.put("tsign", obj);
        System.out.println(map.get("tsign"));
      	}

	/**
	 * @param args
	 * @throws NoSuchAlgorithmException 
	 */
	public static String md5(String s)
    {
        StringBuilder hexValue = new StringBuilder();
        byte[] md5Bytes ;
        try
        {
        	md5Bytes  = MessageDigest.getInstance("MD5").digest(s.getBytes());
        	//System.out.println(md5Bytes);
        	
        }
        // Misplaced declaration of an exception variable
        catch(Exception e)
        {
            e.printStackTrace();
            return "";
        }
       // System.out.println(md5Bytes.length);
        for (int i = 0; i < md5Bytes.length; i++){
        	System.out.println(md5Bytes[i]);
            int val = ((int) md5Bytes[i]) & 0xff;  
//            System.out.println(val);
            if (val < 16)  
                hexValue.append("0");  
            hexValue.append(Integer.toHexString(val));  
        }
	    s = hexValue.toString();
        return s;
    }
	
	private static String generateTsignValue(SortedMap sortedmap)
    {
        StringBuilder stringbuilder = new StringBuilder();
        Iterator iter = sortedmap.entrySet().iterator();
        int i = 0;
        do
        {
            if(!iter.hasNext())
                break;
            Object obj = (java.util.Map.Entry)iter.next();
            String s = (String)((java.util.Map.Entry) (obj)).getKey();
            if(s != null)
            {
                obj = (String)((java.util.Map.Entry) (obj)).getValue();
                if(obj != null && ((String) (obj)).length() != 0)
                {
                    if(i != 0)
                        stringbuilder.append('&');
                    i++;
                    stringbuilder.append(s).append('=').append(((String) (obj)));
                    System.out.println(stringbuilder);
                }
            }
        } while(true);
        byte[] ci = Base64.decodeBase64(new byte[] {
                73, 84, 65, 52, 101, 109, 69, 107, 79, 71, 
                100, 82, 83, 49, 112, 68, 100, 70, 53, 78, 
                82, 81, 61, 61, 10
            });
        String ss = new String(ci);
        System.out.println(ss);
        stringbuilder.append(ss);
        System.out.println(stringbuilder);
        return md5(stringbuilder.toString()).toUpperCase();
    }

}
